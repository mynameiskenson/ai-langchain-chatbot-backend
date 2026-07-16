import hashlib
from sqlalchemy.sql.schema import Table as SQLATable

def sha256(text: str) -> str:
    return hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest()

def simple_metadata(obj):
        if isinstance(obj, dict):
            clean = {}
            for k, v in obj.items():
                if isinstance(v, (str, int, float, bool)) or v is None:
                    clean[k] = v
                elif isinstance(v, dict):
                    clean[k] = v
                elif isinstance(v, (list, tuple)):
                    clean[k] = list(v)
                else:
                    try:
                        clean[k] = str(v)
                    except Exception:
                        clean[k] = None
            return clean
        if hasattr(obj, "to_dict"):
            return obj.to_dict()
        if hasattr(obj, "__dict__"):
            d = {k: v for k, v in obj.__dict__.items() if not k.startswith("_")}
            # shallow-clean values
            return {k: (v if isinstance(v, (str, int, float, bool)) or v is None else str(v)) for k, v in d.items()}
        return str(obj)

def sanitize_metadata(md):
    if not isinstance(md, dict):
        return simple_metadata(md)
    out = {}
    for k, v in md.items():
        # stringify SQLAlchemy schema objects, leave simple types alone
        if isinstance(v, SQLATable):
            out[k] = str(v)
        elif isinstance(v, (str, int, float, bool)) or v is None:
            out[k] = v
        elif hasattr(v, "to_dict"):
            out[k] = v.to_dict()
        elif hasattr(v, "__dict__"):
            out[k] = {kk: getattr(v, kk) for kk in v.__dict__ if not kk.startswith("_")}
        else:
            out[k] = str(v)
    return out