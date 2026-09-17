from providers.factory import get_railway_provider

_provider = None

def railway_provider():
    global _provider
    if _provider is None:
        _provider = get_railway_provider()
    return _provider

def reset_provider():
    global _provider
    _provider = None
