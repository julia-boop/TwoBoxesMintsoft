from dotenv import load_dotenv
from datetime import datetime, timezone
from pathlib import Path
import os
import json

from mappers.mintsoft_mapper import map_client, map_warehouse

load_dotenv()

def map_return(data):
    data = data[0]["event_data"]
    merchant_name = data["merchant_integration"]["merchant"]["name"]
    client_id = map_client(merchant_name)
    warehouse_id = map_warehouse(merchant_name)
    # m_items = []
    # for item in data["line_items"]:
    #     m_items.append({
    #         "SKU": item["sku"],
    #         "Quantity": item["quantity"],
    #         "ReturnReasonId": 1,
    #         "Action": "DoNothing",
    #         "Comments": item["graded_attributes"][0]["merchant_grading_attribute"]["grading_attribute"]["title"]
    #     })

    m_data = {
        "ClientId": client_id,
        "WarehouseId": warehouse_id,
        "Reference": data["line_items"][0]["tracking_number"],

    }
    return m_data