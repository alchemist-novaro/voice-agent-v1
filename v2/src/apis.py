import json
from typing import Callable, Any

customer_info = {
    "full_name": "Millie Dowe",
    "phone_number": "5301504321",
    "email_address": "Millie.dowe@example.com",
    "addresses": [
        {
            "address": "428 Seawind Street, Lakeway, TX 78734",
            "is_authorized": True,
            "property_type": "house",
            "type": "residential",
            "in_service_area": True,
            "serviceable": True
        }
    ]
}
customer_status = {
    "greeting": False,
    "service_address": False,
    "service_information": False,
    "property": False,
    "dispatch": False
}

with open('./data/services.json') as f:
    services: list[Any] = json.load(f)

def get_contact_information(customer_id: str, args: Any):
    return {
        "full_name": customer_info.get("full_name", None),
        "phone_number": customer_info.get("phone_number", None),
        "email_address": customer_info.get("email_address", None)
    }

def get_service_addresses(customer_id: str, args: Any):
    return {
        "addresses": [service["address"] for service in customer_info.get("addresses", [])]
    }

def set_contact_information(customer_id: str, args: Any):
    print(f"contact customer information is set. customer id: {customer_id}")

def update_contact_information(customer_id: str, args: Any):
    info_data = args["update_contact_information"]
    if not info_data["updatable"]:
        return {
            "status": "failed"
        }

    if info_data["full_name"]:
        customer_info["full_name"] = info_data["full_name"]
    if info_data["phone_number"]:
        customer_info["phone_number"] = info_data["phone_number"]
    if info_data["email_address"]:
        customer_info["email_address"] = info_data["email_address"]

    if not customer_info["full_name"] and not customer_info["phone_number"]:
        return {
            "status": "all_missed"
        }
    elif not customer_info["full_name"] or not customer_info["phone_number"]:
        return {
            "status": "some_missed"
        }
    else:
        set_contact_information(customer_id, args)
        return {
            "status": "full"
        }

def update_customer_status(customer_id: str, args: Any):
    customer_status["greeting"] = True

def get_customer_status(customer_id: str, args: Any):
    return customer_status

def finish_greeting_agent(customer_id: str, args: Any):
    customer_status["service_addresses"] = True
    print("Greeting Agent finished")

def finish_service_agent(customer_id: str, args: Any):
    customer_status["service_information"] = True
    print("Service Agent finished")

def validate_service_address(customer_id: str, args: Any):
    address_data = args["update_service_address"]
    if not address_data["service_address"]:
        return {
            "validated": False
        }
    current_addresses = [service["address"] for service in customer_info["addresses"]]
    if address_data["service_address"] in current_addresses:
        customer_info["addresses"].append(
            {
                "address": address_data["service_address"],
                "is_authorized": True,
                "property_type": "house",
                "type": "residential",
                "in_service_area": True,
                "serviceable": True
            }
        )
    return {
        "validated": True
    }

def get_services(customer_id: str, args: Any):
    seen = set()
    service_list = []
    for service in services:
        item = {
            "trade": service["trade"],
            "serviceable_type": service["serviceable_type"],
            "service_type": service["service_type"],
        }
        # convert dict to tuple for hashability
        key = (item["trade"], item["serviceable_type"], item["service_type"])
        if key not in seen:
            seen.add(key)
            service_list.append(item)
    return service_list

def check_service(customer_id: str, args: Any):
    _service = args["service"]
    for service in services:
        if _service["trade"] == service["trade"] and \
            _service["serviceable_type"] == service["serviceable_type"] and \
            _service["service_type"] == service["service_type"]:
            customer_info["service"] = {
                "support": "support" if service["is_overbookable"] else "some_support",
                "qualification_questions": [{
                    "question": question,
                    "answered": False,
                    "answer": "",
                } for question in service["qualification_questions"]]
            }
            return customer_info["service"]
    customer_info["service"] = {
        "support": "not_support",
        "qualification_questions": []
    }

def get_qualification_question(customer_id: str, args: Any):
    for question in customer_info["service"]["qualification_questions"]:
        if not question["answered"]:
            return question
    return {
        "answered": None
    }

def save_qualification_answer(customer_id: str, args: Any):
    question_text = args["qualification_question"]["question"]
    answer_text = args["message"]

    for question in customer_info["service"]["qualification_questions"]:
        if question["question"] == question_text and not question["answered"]:
            question["answered"] = True
            question["answer"] = answer_text


API_FUNCTIONS: dict[str, Callable[[str, Any], Any]] = {
    "get_contact_information":      get_contact_information,
    "get_service_addresses":        get_service_addresses,
    "set_contact_information":      set_contact_information,
    "update_contact_information":   update_contact_information,
    "update_customer_status":       update_customer_status,
    "get_customer_status":          get_customer_status,
    "finish_greeting_agent":        finish_greeting_agent,
    "validate_service_address":     validate_service_address,
    "get_services":                 get_services,
    "check_service":                check_service,
    "get_qualification_question":   get_qualification_question,
    "save_qualification_answer":    save_qualification_answer,
    "finish_service_agent":         finish_service_agent
}