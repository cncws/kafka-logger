import logging
import socket
from contextlib import contextmanager
from contextvars import ContextVar


def get_host_ip() -> str:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            ip, _ = s.getsockname()
            return ip
    except Exception:
        return "127.0.0.1"


_host_ip = get_host_ip()
_trace_id_ctx = ContextVar("trace_id", default="")


@contextmanager
def set_trace_id(trace_id: str):
    token = _trace_id_ctx.set(trace_id)
    try:
        yield
    finally:
        _trace_id_ctx.reset(token)


def get_trace_id() -> str:
    return _trace_id_ctx.get()


class HostInjectFilter(logging.Filter):
    def __init__(self, name="", *, bind_key: str = "host"):
        super().__init__(name)
        self._key = bind_key

    def filter(self, record: logging.LogRecord) -> bool:
        setattr(record, self._key, _host_ip)
        return True


class TraceIdInjectFilter(logging.Filter):
    """为日志记录注入 trace_id 属性"""

    def __init__(self, name="", *, bind_key: str = "trace_id"):
        super().__init__(name)
        self._key = bind_key

    def filter(self, record: logging.LogRecord) -> bool:
        setattr(record, self._key, get_trace_id())
        return True
