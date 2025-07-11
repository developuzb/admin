import json
import os


def get_services():
    with open("admin/services/json/services.json", "r", encoding="utf-8") as f:
        return json.load(f)


def create_click_url(order_id, amount):
    return f"https://my.click.uz/pay/?service_id=999999999&merchant_id=398062629&amount={amount}&transaction_param={order_id}"
