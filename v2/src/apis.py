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

def get_contact_information(customer_id: str, args: Any):
    return {
        "full_name": customer_info.get("full_name", None),
        "phone_number": customer_info.get("phone_number", None),
        "email_address": customer_info.get("email_address", None)
    }

def get_addresses(customer_id: str, args: Any):
    return {
        "addresses": customer_info.get("addresses", [])
    }

def set_contact_information(customer_id: str, args: Any):
    print(f"contact customer information is set. customer id: {customer_id}")

def update_contact_information(customer_id: str, args: Any):
    info_data = args["update_contact_customer_information_data"]
    if info_data["full_name"]:
        customer_info["full_name"] = info_data["full_name"]
    if info_data["phone_number"]:
        customer_info["phone_number"] = info_data["phone_number"]
    if info_data["email_address"]:
        customer_info["email_address"] = info_data["email_address"]

    if not customer_info["full_name"] or not customer_info["phone_number"]:
        return {
            "status": "failed"
        }
    else:
        set_contact_customer_information(customer_id, args)
        return {
            "status": "success"
        }

API_FUNCTIONS: dict[str, Callable[[str, Any], Any]] = {
    "get_contact_information": get_contact_information,
    "get_addresses": get_addresses,
    "set_contact_information": set_contact_information,
    "update_contact_information": update_contact_information
}