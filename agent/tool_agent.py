import json
import ollama

from agent.schemas import TravelRequest
from tools.train_search import search_trains
from tools.recommendation import (
    recommend_trains,
    filter_before_arrival,
)
from tools.train_status import get_train_status, get_train_route
from tools.pnr_status import get_pnr_status


MODEL = "llama3.2"


class RailMateToolAgent:

    def __init__(self):

        self.messages = []

        self.current_request = TravelRequest()

        self.last_trains = []

        self.last_availability = {}

        self.last_recommendations = []

    # ==========================================================
    # TOOL: SEARCH TRAINS
    # ==========================================================

    def tool_search_trains(
        self,
        origin: str,
        destination: str,
    ):

        print(
            "\n🔎 SEARCH_TRAINS"
        )

        print(
            f"   Route: {origin} → {destination}"
        )

        trains = search_trains(
            origin,
            destination,
        )

        self.last_trains = trains

        print(
            f"   Found: {len(trains)} trains"
        )

        return {
            "success": True,
            "count": len(trains),

            "trains": [

                {
                    "train_number":
                        train["train_number"],

                    "train_name":
                        train["train_name"],

                    "departure":
                        train["departure"],

                    "arrival":
                        train["arrival"],

                    "duration":
                        train["duration"],

                    "availability":
                        train["availability"],

                    "fares":
                        train["fares"],
                }

                for train in trains
            ],
        }

    # ==========================================================
    # TOOL: CHECK AVAILABILITY
    # ==========================================================

    def tool_check_availability(
        self,
        train_number: str,
        travel_class: str,
    ):

        for train in self.last_trains:

            if str(
                train["train_number"]
            ) == str(train_number):

                availability = train[
                    "availability"
                ].get(
                    travel_class,
                    "NOT AVAILABLE",
                )

                fare = train[
                    "fares"
                ].get(
                    travel_class
                )

                result = {

                    "success": True,

                    "train_number":
                        train_number,

                    "travel_class":
                        travel_class,

                    "availability":
                        availability,

                    "fare_per_passenger":
                        fare,
                }

                self.last_availability[
                    str(train_number)
                ] = result

                print(
                    f"   {train_number} "
                    f"{travel_class}: "
                    f"{availability} "
                    f"₹{fare}"
                )

                return result

        return {

            "success": False,

            "message":
                "Train not found.",
        }

    # ==========================================================
    # TOOL: TRAIN STATUS
    # ==========================================================

    def tool_train_status(self, train_number: str):
        return get_train_status(train_number)

    def tool_train_route(self, train_number: str):
        return get_train_route(train_number)

    # ==========================================================
    # TOOL: PNR STATUS
    # ==========================================================

    def tool_pnr_status(self, pnr: str):
        return get_pnr_status(pnr)

    # ==========================================================
    # TOOL: GET TRAIN DETAILS
    # ==========================================================

    def tool_get_train_details(
        self,
        train_number: str,
    ):

        for train in self.last_trains:

            if str(
                train["train_number"]
            ) == str(train_number):

                return {

                    "success": True,

                    "train": train,
                }

        return {

            "success": False,

            "message":
                "Train not found.",
        }

    # ==========================================================
    # TOOL: RECOMMEND
    # ==========================================================

    def tool_recommend_trains(
        self,
        travel_class: str,
        passengers: int,
        preference: str = None,
        arrival_before: str = None,
    ):

        # ------------------------------------------------------
        # SAFETY CHECK
        # ------------------------------------------------------

        if not self.last_trains:

            print(
                "\n⚠ Recommendation blocked:"
                " search_trains() has not run."
            )

            return {

                "success": False,

                "error":
                    "SEARCH_REQUIRED",

                "message":
                    "Search trains before recommending.",
            }

        print(
            "\n🧠 RECOMMEND_TRAINS"
        )

        # recommend_trains() is responsible only for deterministic
        # ranking. Arrival deadlines are applied separately.
        results = recommend_trains(
            trains=self.last_trains,
            travel_class=travel_class,
            passengers=int(passengers),
            preference=preference,
        )

        if arrival_before:
            results = filter_before_arrival(
                results,
                arrival_before,
            )

        self.last_recommendations = results

        print(
            f"   Ranked: {len(results)} trains"
        )

        return {

            "success": True,

            "recommendations": [

                {

                    "rank":
                        index + 1,

                    "train_number":
                        r["train_number"],

                    "train_name":
                        r["train_name"],

                    "departure":
                        r["departure"],

                    "arrival":
                        r["arrival"],

                    "duration":
                        r["duration"],

                    "travel_class":
                        r["travel_class"],

                    "availability":
                        r["availability"],

                    "fare_per_passenger":
                        r["fare_per_passenger"],

                    "total_fare":
                        r["total_fare"],

                    "score":
                        r["score"],
                }

                for index, r
                in enumerate(results)
            ],
        }

    # ==========================================================
    # TOOL DEFINITIONS
    # ==========================================================

    def get_tools(self):

        return [

            {
                "type": "function",

                "function": {

                    "name":
                        "search_trains",

                    "description":
                        """
Search railway trains between
an origin and destination.

This is the FIRST railway
tool that must be used.
""",

                    "parameters": {

                        "type":
                            "object",

                        "properties": {

                            "origin": {
                                "type":
                                    "string"
                            },

                            "destination": {
                                "type":
                                    "string"
                            },
                        },

                        "required": [

                            "origin",

                            "destination",
                        ],
                    },
                },
            },

            {
                "type": "function",

                "function": {

                    "name":
                        "check_availability",

                    "description":
                        """
Check railway availability and
fare for a train and class.

Use only AFTER search_trains.
""",

                    "parameters": {

                        "type":
                            "object",

                        "properties": {

                            "train_number": {
                                "type":
                                    "string"
                            },

                            "travel_class": {
                                "type":
                                    "string"
                            },
                        },

                        "required": [

                            "train_number",

                            "travel_class",
                        ],
                    },
                },
            },

            {
                "type": "function",

                "function": {

                    "name":
                        "get_train_details",

                    "description":
                        """
Get details of a train.

Use only AFTER search_trains.
""",

                    "parameters": {

                        "type":
                            "object",

                        "properties": {

                            "train_number": {
                                "type":
                                    "string"
                            },
                        },

                        "required": [
                            "train_number"
                        ],
                    },
                },
            },

            {
                "type": "function",
                "function": {
                    "name": "train_status",
                    "description": "Get DEMO operational status for a train number.",
                    "parameters": {
                        "type": "object",
                        "properties": {"train_number": {"type": "string"}},
                        "required": ["train_number"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "train_route",
                    "description": "Get DEMO route and stop information for a train number.",
                    "parameters": {
                        "type": "object",
                        "properties": {"train_number": {"type": "string"}},
                        "required": ["train_number"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "pnr_status",
                    "description": "Get DEMO PNR status. Use only for clearly supplied PNR numbers.",
                    "parameters": {
                        "type": "object",
                        "properties": {"pnr": {"type": "string"}},
                        "required": ["pnr"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name":
                        "recommend_trains",

                    "description":
                        """
Rank trains using the Python
recommendation engine.

IMPORTANT:
search_trains must be completed
before this tool can work.
""",

                    "parameters": {

                        "type":
                            "object",

                        "properties": {

                            "travel_class": {
                                "type":
                                    "string"
                            },

                            "passengers": {
                                "type":
                                    "integer"
                            },

                            "preference": {
                                "type": [
                                    "string",
                                    "null"
                                ]
                            },

                            "arrival_before": {
                                "type": [
                                    "string",
                                    "null"
                                ]
                            },
                        },

                        "required": [

                            "travel_class",

                            "passengers",
                        ],
                    },
                },
            },
        ]

    # ==========================================================
    # AGENT STEP
    # ==========================================================

    def llm_step(self):

        response = ollama.chat(

            model=MODEL,

            messages=self.messages,

            tools=self.get_tools(),
        )

        message = response["message"]

        tool_calls = message.get(
            "tool_calls"
        )

        if not tool_calls:

            return message.get(
                "content",
                "",
            )

        self.messages.append(
            message
        )

        for tool_call in tool_calls:

            function = tool_call[
                "function"
            ]

            name = function[
                "name"
            ]

            arguments = function.get(
                "arguments",
                {},
            )

            print(
                f"\n🔧 Agent tool call: {name}"
            )

            print(
                f"   Arguments: {arguments}"
            )

            result = self.execute_tool(

                name,

                arguments,
            )

            self.messages.append(

                {

                    "role":
                        "tool",

                    "content":
                        json.dumps(
                            result,
                            default=str,
                        ),
                }
            )

        return None

    # ==========================================================
    # EXECUTOR
    # ==========================================================

    def execute_tool(
        self,
        name,
        arguments,
    ):

        if name == "search_trains":

            return self.tool_search_trains(
                **arguments
            )

        elif name == "check_availability":

            # Prevent availability before search
            if not self.last_trains:

                return {

                    "success": False,

                    "error":
                        "SEARCH_REQUIRED",

                    "message":
                        "Run search_trains first.",
                }

            return self.tool_check_availability(
                **arguments
            )

        elif name == "get_train_details":

            if not self.last_trains:

                return {

                    "success": False,

                    "error":
                        "SEARCH_REQUIRED",

                    "message":
                        "Run search_trains first.",
                }

            return self.tool_get_train_details(
                **arguments
            )

        elif name == "train_status":
            return self.tool_train_status(**arguments)

        elif name == "train_route":
            return self.tool_train_route(**arguments)

        elif name == "pnr_status":
            return self.tool_pnr_status(**arguments)

        elif name == "recommend_trains":

            return self.tool_recommend_trains(
                **arguments
            )

        return {

            "success": False,

            "error":
                "UNKNOWN_TOOL",
        }

    # ==========================================================
    # MAIN CONTROLLED AGENT
    # ==========================================================

    def run(
        self,
        user_message: str,
        request: TravelRequest,
    ):

        self.current_request = request

        self.last_trains = []

        self.last_availability = {}

        self.last_recommendations = []

        system_prompt = f"""
You are RailMate, an Indian
railway travel AI agent.

Today's date:
2026-09-15

CURRENT TRAVEL REQUEST:

{request.model_dump_json(indent=2)}

RAILWAY DATA:
DEMO DATA ONLY.

NEVER invent railway information.

STATUS AND PNR DATA ARE DEMO ONLY.
Use train_status, train_route, or pnr_status only when the user explicitly asks for them.

MANDATORY WORKFLOW:

STEP 1:
Call search_trains using the
origin and destination.

STEP 2:
After search_trains returns,
use check_availability for the
requested class where useful.

STEP 3:
After the search is complete,
call recommend_trains.

STEP 4:
Use the recommendation result
to explain the best train.

IMPORTANT:

Never call recommend_trains
before search_trains.

Never invent train numbers.

Never invent fares.

Never invent availability.

Never alter tool results.

Do not book tickets.

Do not request:
passwords,
OTP,
CAPTCHA,
card details,
CVV,
UPI PIN.

Do not make payments.

The Python application is the
final authority for ranking,
availability and fare.
"""

        self.messages = [

            {
                "role":
                    "system",

                "content":
                    system_prompt,
            },

            {
                "role":
                    "user",

                "content":
                    user_message,
            },
        ]

        # ======================================================
        # LET OLLAMA INITIATE TOOL USE
        # ======================================================

        print(
            "\n🤖 Agent is deciding "
            "which tool to use..."
        )

        self.llm_step()

        # ======================================================
        # CONTROLLER ENFORCES SEARCH
        # ======================================================

        if not self.last_trains:

            print(
                "\n🔐 Controller:"
                " enforcing search_trains()."
            )

            self.tool_search_trains(

                request.origin,

                request.destination,
            )

        # ======================================================
        # CONTROLLER CHECKS AVAILABILITY
        # ======================================================

        print(
            "\n🔐 Controller:"
            " checking requested class..."
        )

        for train in self.last_trains:

            self.tool_check_availability(

                train_number=
                    train["train_number"],

                travel_class=
                    request.travel_class,
            )

        # ======================================================
        # CONTROLLER RUNS RECOMMENDATION
        # ======================================================

        print(
            "\n🔐 Controller:"
            " running recommendation..."
        )

        self.tool_recommend_trains(

            travel_class=
                request.travel_class,

            passengers=
                request.passengers,

            preference=
                request.preference,

            arrival_before=
                request.arrival_before,
        )

        # ======================================================
        # FINAL DETERMINISTIC RESULT
        # ======================================================

        if not self.last_recommendations:

            return (
                "No suitable trains were found "
                "for your requirements."
            )

        best = (
            self.last_recommendations[0]
        )

        # ======================================================
        # OLLAMA EXPLAINS ONLY
        # ======================================================

        explanation_prompt = f"""
The Python application has selected
this exact train:

Train:
{best["train_number"]} — {best["train_name"]}

Departure:
{best["departure"]}

Arrival:
{best["arrival"]}

Duration:
{best["duration"]}

Class:
{best["travel_class"]}

Availability:
{best["availability"]}

Fare per passenger:
₹{best["fare_per_passenger"]}

Passengers:
{request.passengers}

Estimated total:
₹{best["total_fare"]}

Score:
{best["score"]}

User preference:
{request.preference}

Explain briefly why this exact
train is recommended.

DO NOT select another train.

DO NOT change any number.

DO NOT change the fare.

DO NOT change availability.

Do not invent information.

Mention that this is DEMO data.
"""

        response = ollama.chat(

            model=MODEL,

            messages=[

                {
                    "role":
                        "system",

                    "content":
                        "Explain the application's "
                        "decision without changing it.",
                },

                {
                    "role":
                        "user",

                    "content":
                        explanation_prompt,
                },
            ],
        )

        explanation = response[
            "message"
        ].get(
            "content",
            "",
        )

        return self.last_recommendations

    # ==========================================================
    # EXPLAIN A DETERMINISTIC RECOMMENDATION
    # ==========================================================

    def explain(self, option):
        """Ask Ollama to explain an already-selected option only."""
        if not option:
            return "No train has been selected for explanation."

        explanation_prompt = f"""
Explain why this exact train was recommended by the Python
application. Do not select or change the train.

Train:
{option["train_number"]} — {option["train_name"]}

Departure:
{option["departure"]}

Arrival:
{option["arrival"]}

Duration:
{option["duration"]}

Class:
{option["travel_class"]}

Availability:
{option["availability"]}

Fare per passenger:
₹{option["fare_per_passenger"]}

Estimated total:
₹{option["total_fare"]}

Agent score:
{option["score"]}

Explain briefly using only these facts.
Mention that the railway information is DEMO data.
Do not invent information.
"""

        response = ollama.chat(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content":
                        "Explain the application's deterministic "
                        "decision without changing any facts."
                },
                {
                    "role": "user",
                    "content": explanation_prompt
                },
            ],
        )

        return response["message"].get("content", "")
