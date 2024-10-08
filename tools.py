import json


class JsonClassEncoder(json.JSONEncoder):
    def default(self, obj):
        # if isinstance(obj, Address):
        # return obj.__dict__
        out={}
        for i_attr in [attr for attr in dir(obj) if not callable(getattr(obj, attr)) and not attr.startswith("_")]:
            out[i_attr]=obj.__getattribute__(i_attr)
        return out
