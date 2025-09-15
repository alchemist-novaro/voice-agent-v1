import queue
from typing import Callable, Any
import openai
import time
from datetime import datetime, timedelta
import threading

class Service:
    time: str | None = None
    area: str | None = None
    type: str | None = None
    building: str | None = None
    rating: int | None = None

service = Service()

input_messages: dict[str, (str, datetime)] = {}
input_required: dict[str, bool] = {}
output_chunks: dict[str, queue.Queue[(Any, datetime)]] = {}
output_finished: dict[str, bool] = {}

class CloseConversation(Exception):
    """Raised when the user wants to quit the conversation."""
    pass

def get_business_information(customer_id: str, args: dict[str, Any]):
    return {
        "business_name": "Uno",
    }

def get_user_request(customer_id: str, args: dict[str, Any]) -> str:
    input_required[customer_id] = True
    while customer_id not in input_messages:
        time.sleep(0.1)
    prompt = input_messages[customer_id][0]
    del input_required[customer_id]
    del input_messages[customer_id]
    if prompt.lower() == "quit":
        raise CloseConversation("User ended the conversation.")
    return prompt

def get_service_type(customer_id: str, args: dict[str, Any]) -> list[str]:
    return [
        "Plumbing",
        "Drain"
    ]

def get_service_area(customer_id: str, args: dict[str, Any]) -> list[str]:
    return [
        "6071 Barker Dr, Waterford, 48329 MI",
        "236 S LOS ANGELES ST APT 321, LOS ANGELES, CA 90012"
    ]

def get_service_building(customer_id: str, args: dict[str, Any]) -> list[str]:
    return [
        "residental",
        "commercial"
    ]

def get_service_times(customer_id: str, args: dict[str, Any]) -> list[str]:
    return [
        "Tuesday, 9 AM",
        "Wednesday, 10 AM",
        "Thursday, 8 AM"
    ]

def get_node_topics(customer_id: str, args: dict[str, Any]) -> dict[int, dict[str, str]]:
    return {
        0: {
            "name": "area_confirm",
            "topic": "Confirm Service Area"
        },
        3: {
            "name": "building_confirm",
            "topic": "Confirm Service Building Type"
        },
        6: {
            "name": "cancel_confirm",
            "topic": "He want to cancel"
        },
        11: {
            "name": "service_confirm",
            "topic": "Confirm Service Type"
        },
        16: {
            "name": "time_schedule",
            "topic": "Schedule Service Time"
        },
        22: {
            "name": "contact_information",
            "topic": "Check Contact Information"
        },
        100: {
            "name": "no_topic",
            "topic": "Not related with any topics"
        }
    }

def output_cmd(customer_id: str, messages: list[dict[str, str]]) -> str:
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        stream=True
    )
    full_response = ""
    for chunk in response:
        if customer_id not in output_chunks:
            output_chunks[customer_id] = queue.Queue()
        output_chunks[customer_id].put((chunk, datetime.now()))
        if chunk.choices[0].delta.content:
            full_response += chunk.choices[0].delta.content
    output_finished[customer_id] = True
    return full_response

def inner_process(customer_id: str, messages: list[dict[str, str]]) -> str:
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        stream=True
    )
    full_response = ""
    for chunk in response:
        if chunk.choices[0].delta.content:
            full_response += chunk.choices[0].delta.content
    return full_response

def input_cmd(customer_id: str) -> str:
    input_required[customer_id] = True
    while customer_id not in input_messages:
        time.sleep(0.1)
    prompt = input_messages[customer_id][0]
    del input_required[customer_id]
    del input_messages[customer_id]
    if prompt.lower() == "quit":
        raise CloseConversation("User ended the conversation.")
    return prompt

def save_scheduled_time(customer_id: str, args: dict[str, Any]):
    scheduled_time = args["scheduled_time"]["scheduled_time"]
    schedule_failed = args["scheduled_time"]["schedule_failed"]
    if not schedule_failed:
        service.time = scheduled_time
        print(f"time confirmed: {scheduled_time}")
    else:
        print(f"client canceled schedule")

def save_request_data(customer_id: str, args: dict[str, Any]):
    data = args["response_analytics"]
    service.area = data["service_area"] if not data["service_area_failed"] else None
    service.type = data["service_type"] if not data["service_type_failed"] else None
    service.building = data["service_building"] if not data["service_building_failed"] else None

def check_status(customer_id: str, args: dict[str, Any]):
    return {
        "full_fit": service.time is not None,
        "service_time_failed": service.time is None
    }

def save_rating(customer_id: str, args: dict[str, Any]):
    service.rating = args["finalize_analysis"]["rating"]
    raise CloseConversation("finished conversation")

API_FUNCTIONS: dict[str, Callable[[str, dict[str, Any]], Any]] = {
    "get_user_request": get_user_request,
    "get_service_type": get_service_type,
    "get_service_area": get_service_area,
    "get_service_building": get_service_building,
    "get_service_times": get_service_times,
    "get_node_topics": get_node_topics,
    "output_cmd": output_cmd,
    "input_cmd": input_cmd,
    "inner_process": inner_process,
    "save_scheduled_time": save_scheduled_time,
    "save_request_data": save_request_data,
    "check_status": check_status,
    "save_rating": save_rating,
    "get_business_information": get_business_information
}

EXPIRY = timedelta(hours=1)

def _clean_dict(d: dict, expiry: timedelta):
    """Remove expired items from a dict of (value, timestamp)."""
    now = datetime.now()
    keys_to_delete = [k for k, (_, ts) in d.items() if now - ts >= expiry]
    for k in keys_to_delete:
        del d[k]

def _clean_output_chunks(chunks: dict[str, list[tuple[Any, datetime]]]):
    """Clean lists of (value, timestamp) inside a dict."""
    now = datetime.now()
    keys_to_delete = []
    for k, items in chunks.items():
        # Keep only fresh items
        fresh_items = [(v, ts) for v, ts in items if now - ts < EXPIRY]
        if fresh_items:
            chunks[k] = fresh_items
        else:
            keys_to_delete.append(k)
    for k in keys_to_delete:
        del chunks[k]

def _background_work():
    while True:
        _clean_dict(input_messages, EXPIRY)
        _clean_output_chunks(output_chunks)
        time.sleep(60)  # run every 1 minute

# Start background worker thread
threading.Thread(target=_background_work, daemon=True).start()