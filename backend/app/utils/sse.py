"""Server-Sent Events (SSE) formatting helpers."""

import json
from typing import Any
from pydantic import BaseModel


def format_sse_event(event: str, data: Any) -> str:
    """Format an SSE frame matching W3C EventSource specifications.

    Yields format:
        event: <event_name>\n
        data: <json_string>\n\n
    """
    if isinstance(data, BaseModel):
        data_str = data.model_dump_json()
    elif isinstance(data, list):
        clean_list = [item.model_dump() if isinstance(item, BaseModel) else item for item in data]
        data_str = json.dumps(clean_list, ensure_ascii=False)
    elif isinstance(data, dict):
        clean_dict = {k: (v.model_dump() if isinstance(v, BaseModel) else v) for k, v in data.items()}
        data_str = json.dumps(clean_dict, ensure_ascii=False)
    elif isinstance(data, str):
        data_str = data
    else:
        data_str = json.dumps(data, ensure_ascii=False)

    return f"event: {event}\ndata: {data_str}\n\n"
