# aicp/utils.py
import json, logging, uuid
from datetime import datetime, timezone

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def gen_id(prefix: str = "") -> str:
    return (prefix + "-" if prefix else "") + uuid.uuid4().hex

class JsonFormatter(logging.Formatter):
    def format(self, record):
        base = {
            "ts": now_iso(),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        if hasattr(record, "extra") and isinstance(record.extra, dict):
            base.update(record.extra)
        return json.dumps(base, ensure_ascii=False)

def setup_logging(level="INFO"):
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.setLevel(level)
    root.handlers = [handler]
