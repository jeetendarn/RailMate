from datetime import datetime
import re
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from agent.agent import extract_request, missing_information, generate_question
from agent.schemas import TravelRequest
from agent.tool_agent import RailMateToolAgent
from tools.train_status import get_train_status, get_train_route
from tools.pnr_status import get_pnr_status


app = FastAPI(title="RailMate AI", version="1.0.0")


class ChatInput(BaseModel):
    message: str


class Passenger(BaseModel):
    name: str
    age: int
    gender: str
    berth_preference: str


class SelectInput(BaseModel):
    train_number: str


class PassengerInput(BaseModel):
    passengers: list[Passenger]


class SessionState:
    def __init__(self):
        self.request = TravelRequest()
        self.agent = RailMateToolAgent()
        self.recommendations: list[dict[str, Any]] = []
        self.selected_option: dict[str, Any] | None = None
        self.passengers: list[dict[str, Any]] = []
        self.last_booking: dict[str, Any] | None = None

    def reset(self):
        self.request = TravelRequest()
        self.agent = RailMateToolAgent()
        self.recommendations = []
        self.selected_option = None
        self.passengers = []
        self.last_booking = None


# Single-session DEMO state. For production, replace with per-user/session storage.
state = SessionState()


def booking_transaction(request: TravelRequest, option: dict, passengers: list[dict]) -> dict:
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return {
        "booking_reference": f"RM-DEMO-{timestamp}-{option['train_number']}",
        "status": "READY_FOR_PROVIDER_HANDOFF",
        "mode": "DEMO",
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "journey": {
            "origin": request.origin,
            "destination": request.destination,
            "journey_date": request.journey_date,
        },
        "train": {
            "train_number": option["train_number"],
            "train_name": option["train_name"],
            "departure": option["departure"],
            "arrival": option["arrival"],
            "duration": option["duration"],
            "travel_class": option["travel_class"],
            "availability": option["availability"],
        },
        "passengers": passengers,
        "fare": {
            "fare_per_passenger": option["fare_per_passenger"],
            "passenger_count": len(passengers),
            "estimated_total": option["total_fare"],
        },
    }


def response(message: str, **extra):
    data = {"message": message, "demo": True}
    data.update(extra)
    return data


HTML = r"""
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>RailMate AI</title>
<style>
*{box-sizing:border-box}body{margin:0;font-family:Segoe UI,Arial,sans-serif;background:#f4f7fb;color:#172033}
header{background:linear-gradient(135deg,#101b3d,#2454a6);color:white;padding:22px 28px}
header h1{margin:0;font-size:28px}header p{margin:6px 0 0;opacity:.85}
.container{max-width:1180px;margin:22px auto;padding:0 18px}
.notice{background:#fff7df;border:1px solid #f0d27a;padding:12px 16px;border-radius:12px;margin-bottom:18px}
.chat{background:white;border-radius:16px;box-shadow:0 8px 30px #13233d12;padding:18px}
.messages{min-height:120px;max-height:330px;overflow:auto;padding:4px}
.msg{padding:11px 14px;border-radius:12px;margin:9px 0;max-width:85%;white-space:pre-wrap}
.user{background:#e9f0ff;margin-left:auto}.bot{background:#eef2f7}
.controls{display:flex;gap:10px;margin-top:14px}.controls input{flex:1;padding:13px;border:1px solid #cbd3df;border-radius:10px;font-size:15px}
button{border:0;border-radius:10px;padding:12px 17px;background:#2454a6;color:#fff;cursor:pointer;font-weight:600}
button.secondary{background:#667085}button.danger{background:#b42318}
h2{margin-top:24px}.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:15px}
.card{background:#fff;border-radius:15px;padding:17px;box-shadow:0 5px 20px #13233d10;border:1px solid #e1e6ee}
.card h3{margin:0 0 5px}.muted{color:#667085}.fare{font-size:20px;font-weight:700;margin:10px 0}.badge{display:inline-block;padding:4px 8px;border-radius:99px;background:#e7f6ec;color:#087443;font-size:12px;font-weight:700}
.panel{background:white;border-radius:15px;padding:18px;margin-top:18px;box-shadow:0 5px 20px #13233d10}
.formrow{display:grid;grid-template-columns:2fr 1fr 1fr 1.5fr;gap:9px;margin:9px 0}.formrow input,.formrow select{padding:10px;border:1px solid #cbd3df;border-radius:8px}
.hidden{display:none}.summary{line-height:1.7}.small{font-size:13px;color:#667085}
@media(max-width:700px){.formrow{grid-template-columns:1fr}.controls{flex-direction:column}}
</style>
</head>
<body>
<header><h1>🚆 RailMate AI</h1><p>Local AI railway assistant • Ollama + Llama 3.2</p></header>
<div class="container">
<div class="notice">⚠ <b>DEMO MODE:</b> Railway schedules, fares, availability, PNR and operational information are sample data. Live booking is not connected.</div>

<div class="chat">
<div id="messages" class="messages">
<div class="msg bot">Hello! Tell me your journey naturally, for example: <b>Mysore to Chennai, September 21, 2 people, 2A, evening.</b></div>
</div>
<div class="controls">
<input id="message" placeholder="e.g. Mysore to Chennai on September 21 for 2 people in 2A">
<button onclick="send()">Send</button>
</div>
<div class="controls">
<button class="secondary" onclick="sendText('help')">Help</button>
<button class="secondary" onclick="sendText('show my last booking')">Last booking</button>
<button class="secondary" onclick="sendText('start a new search')">New search</button>
</div>
</div>

<div id="resultsPanel" class="panel hidden">
<h2>🚆 Train Options</h2><div id="results" class="cards"></div>
</div>

<div id="passengerPanel" class="panel hidden">
<h2>👤 Passenger Details</h2>
<p class="small">Demo only. Do not enter passwords, OTPs, CAPTCHA, card details, CVV or UPI PIN.</p>
<div id="passengers"></div>
<button onclick="submitPassengers()">Continue to Booking Review</button>
</div>

<div id="reviewPanel" class="panel hidden">
<h2>🎫 Booking Review</h2><div id="review"></div>
<button onclick="confirmBooking()">Confirm Demo Booking</button>
<button class="secondary" onclick="hide('reviewPanel')">Go Back</button>
</div>

<div id="bookingPanel" class="panel hidden">
<h2>🎫 Booking Summary</h2><div id="booking" class="summary"></div>
</div>
</div>

<script>
const $=id=>document.getElementById(id);
function add(who,text){const d=document.createElement('div');d.className='msg '+who;d.innerHTML=text;$('messages').appendChild(d);$('messages').scrollTop=$('messages').scrollHeight}
function hide(id){$(id).classList.add('hidden')}
function show(id){$(id).classList.remove('hidden')}
function esc(s){return String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}

async function send(){const x=$('message');const m=x.value.trim();if(!m)return;x.value='';await sendText(m)}
async function sendText(m){
 add('user',esc(m));
 try{
  const r=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:m})});
  const d=await r.json(); if(!r.ok) throw new Error(d.detail||'Request failed');
  add('bot',esc(d.message));
  if(d.recommendations) renderResults(d.recommendations);
  if(d.booking) renderBooking(d.booking);
 }catch(e){add('bot','❌ '+esc(e.message))}
}

function renderResults(items){
 show('resultsPanel'); hide('passengerPanel');hide('reviewPanel');
 $('results').innerHTML=items.map(x=>`
 <div class="card">
  <h3>${esc(x.train_number)} — ${esc(x.train_name)}</h3>
  <div class="muted">${esc(x.departure)} → ${esc(x.arrival)} · ${esc(x.duration)}</div>
  <p><span class="badge">${esc(x.availability)}</span> &nbsp; ${esc(x.travel_class)}</p>
  <div class="fare">₹${esc(x.fare_per_passenger)} <span class="muted" style="font-size:13px">per passenger</span></div>
  <div class="muted">Total: ₹${esc(x.total_fare)} · Score: ${esc(x.score)}</div>
  <br><button onclick="selectTrain('${esc(x.train_number)}')">Select</button>
 </div>`).join('');
}

async function selectTrain(n){
 const r=await fetch('/api/select',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({train_number:n})});
 const d=await r.json();if(!r.ok){add('bot','❌ '+esc(d.detail));return}
 add('bot',esc(d.message)); renderPassengerForm(d.count);
}

function renderPassengerForm(count){
 show('passengerPanel');hide('reviewPanel');
 $('passengers').innerHTML=Array.from({length:count},(_,i)=>`
 <div class="formrow">
  <input id="pname${i}" placeholder="Passenger ${i+1} name">
  <input id="page${i}" type="number" min="1" max="120" placeholder="Age">
  <select id="pgender${i}"><option>Male</option><option>Female</option><option>Other</option></select>
  <select id="pberth${i}"><option>Lower</option><option>Upper</option><option>Middle</option><option>Side Lower</option><option>Side Upper</option><option>No Preference</option></select>
 </div>`).join('');
}

async function submitPassengers(){
 const rows=[...document.querySelectorAll('[id^=pname]')].map((_,i)=>({
  name:$('pname'+i).value.trim(),age:Number($('page'+i).value),
  gender:$('pgender'+i).value,berth_preference:$('pberth'+i).value
 }));
 const r=await fetch('/api/passengers',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({passengers:rows})});
 const d=await r.json();if(!r.ok){add('bot','❌ '+esc(d.detail));return}
 $('review').innerHTML=reviewHtml(d);
 show('reviewPanel');hide('passengerPanel');
}
function reviewHtml(d){
 const t=d.train, q=d.request;
 return `<div class="summary"><b>${esc(t.train_number)} — ${esc(t.train_name)}</b><br>
 ${esc(q.origin)} → ${esc(q.destination)} · ${esc(q.journey_date)}<br>
 ${esc(t.departure)} → ${esc(t.arrival)} · ${esc(t.duration)}<br>
 Class: <b>${esc(t.travel_class)}</b> · Availability: <b>${esc(t.availability)}</b><br>
 Fare: ₹${esc(t.fare_per_passenger)} × ${d.passengers.length} = <b>₹${esc(t.total_fare)}</b>
 <h3>Passengers</h3>${d.passengers.map((p,i)=>`${i+1}. ${esc(p.name)} · ${esc(p.age)} · ${esc(p.gender)} · ${esc(p.berth_preference)}`).join('<br>')}
 <hr><span class="small">This is a demo review. Actual authentication, OTP, CAPTCHA and payment must be handled by an authorized provider.</span></div>`;
}
async function confirmBooking(){
 const r=await fetch('/api/confirm',{method:'POST'});const d=await r.json();if(!r.ok){add('bot','❌ '+esc(d.detail));return}
 renderBooking(d.booking); add('bot','Demo booking prepared. Secure provider handoff boundary reached.');
 hide('reviewPanel');
}
function renderBooking(b){
 show('bookingPanel');
 $('booking').innerHTML=`<b>Booking Reference:</b> ${esc(b.booking_reference)}<br>
 <b>Status:</b> ${esc(b.status)}<br><b>Mode:</b> DEMO<br><br>
 <b>Journey:</b> ${esc(b.journey.origin)} → ${esc(b.journey.destination)}<br>
 <b>Date:</b> ${esc(b.journey.journey_date)}<br>
 <b>Train:</b> ${esc(b.train.train_number)} — ${esc(b.train.train_name)}<br>
 <b>Departure:</b> ${esc(b.train.departure)} · <b>Arrival:</b> ${esc(b.train.arrival)}<br>
 <b>Class:</b> ${esc(b.train.travel_class)}<br>
 <b>Passengers:</b> ${b.fare.passenger_count}<br>
 <b>Estimated Total:</b> ₹${esc(b.fare.estimated_total)}<br><br>
 ⚠ This is a DEMO transaction, not a railway ticket.`;
}
$('message').addEventListener('keydown',e=>{if(e.key==='Enter')send()});
</script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
def home():
    return HTMLResponse(HTML)


@app.post("/api/chat")
def chat(payload: ChatInput):
    message = payload.message.strip()
    if not message:
        raise HTTPException(400, "Message is required.")

    normalized = message.lower().strip()

    if normalized in {"help", "menu", "options"}:
        return response(
            "You can ask naturally:\n"
            "• Mysore to Chennai on September 21 for 2 people in 2A\n"
            "• Show status of train 16221\n"
            "• Show route of train 16221\n"
            "• Check PNR 1234567890\n"
            "• Show my last booking\n"
            "• Start a new search"
        )

    if normalized in {"start a new search", "new search", "search again", "book another train"}:
        state.reset()
        return response("New search started. What journey would you like to search?")

    if normalized in {"show my last booking", "show last booking", "my last booking", "last booking"}:
        if not state.last_booking:
            return response("There is no booking in this demo session.")
        return response("Here is the latest demo booking.", booking=state.last_booking)

    pnr = re.search(r"\b\d{10}\b", message)
    train = re.search(r"\b\d{5}\b", message)

    if pnr and ("pnr" in normalized or "ticket" in normalized):
        result = get_pnr_status(pnr.group(0))
        return response(
            result.get("message", "PNR result returned.") if not result.get("success") else
            f"PNR {result['pnr']} — Train {result['train_number']} — "
            f"{result['status']} — Coach {result['coach']} — Berth(s): {', '.join(result['berths'])}",
            operational=result,
        )

    if train and any(k in normalized for k in ("route", "stops", "stations")):
        result = get_train_route(train.group(0))
        if not result.get("success"):
            return response(result.get("message", "Train not found."), operational=result)
        return response(
            f"Train {result['train_number']} route:\n" + " → ".join(result["stops"]),
            operational=result,
        )

    if train and any(k in normalized for k in ("status", "running", "delay", "delayed", "on time", "platform")):
        result = get_train_status(train.group(0))
        if not result.get("success"):
            return response(result.get("message", "Train not found."), operational=result)
        return response(
            f"Train {result['train_number']}: {result['status']}\n"
            f"Delay: {result['delay_minutes']} minutes\n"
            f"Expected departure: {result['expected_departure']}\n"
            f"Expected arrival: {result['expected_arrival']}\n"
            f"Platform: {result['platform']}",
            operational=result,
        )

    state.request = extract_request(message, state.request)
    missing = missing_information(state.request)

    if missing:
        return response(
            generate_question(missing),
            request=state.request.model_dump(),
        )

    try:
        results = state.agent.run(message, state.request)
    except Exception as exc:
        raise HTTPException(500, f"RailMate agent error: {exc}") from exc

    if not isinstance(results, list):
        results = state.agent.last_recommendations

    state.recommendations = results or []

    if not state.recommendations:
        return response(
            "I could not find matching trains in the demo dataset.",
            request=state.request.model_dump(),
        )

    return response(
        f"I found {len(state.recommendations)} matching demo train options.",
        request=state.request.model_dump(),
        recommendations=state.recommendations,
    )


@app.post("/api/select")
def select_train(payload: SelectInput):
    for option in state.recommendations:
        if str(option["train_number"]) == str(payload.train_number):
            state.selected_option = option
            return response(
                f"Train {option['train_number']} selected. Please enter passenger details.",
                count=state.request.passengers or 1,
                selected=option,
            )
    raise HTTPException(404, "Train is not in the current result set.")


@app.post("/api/passengers")
def passengers(payload: PassengerInput):
    if not state.selected_option:
        raise HTTPException(400, "Select a train first.")

    expected = state.request.passengers or 1
    if len(payload.passengers) != expected:
        raise HTTPException(400, f"Expected {expected} passenger(s).")

    for p in payload.passengers:
        if not p.name.strip():
            raise HTTPException(400, "Passenger name is required.")
        if p.age < 1 or p.age > 120:
            raise HTTPException(400, "Passenger age must be between 1 and 120.")

    state.passengers = [p.model_dump() for p in payload.passengers]

    return {
        "demo": True,
        "request": state.request.model_dump(),
        "train": state.selected_option,
        "passengers": state.passengers,
    }


@app.post("/api/confirm")
def confirm():
    if not state.selected_option:
        raise HTTPException(400, "Select a train first.")
    if not state.passengers:
        raise HTTPException(400, "Passenger details are required.")

    state.last_booking = booking_transaction(
        state.request,
        state.selected_option,
        state.passengers,
    )
    return response(
        "Demo booking transaction created. It is ready only for an authorized provider handoff.",
        booking=state.last_booking,
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("web_app:app", host="127.0.0.1", port=8000, reload=False)
