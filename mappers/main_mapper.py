from dotenv import load_dotenv
from datetime import datetime, timezone
from pathlib import Path
import os
import json

from mappers.client_mapper import map_client, map_warehouse

load_dotenv()

def map_return(data):
    data = data[0]["event_data"]
    merchant_name = data["merchant_integration"]["merchant"]["name"]
    client_id = map_client(merchant_name)
    warehouse_id = map_warehouse(merchant_name)

    m_data = {
        "ClientId": client_id,
        "WarehouseId": warehouse_id,
        "OrderId": data["line_items"][0]["storefront_order_number"],
        "ReturnReasonId": 1,
        "ReturnItems": [
            {
                "SKU":"",
                "Quantity":1,
                "ReturnReasonId":1,
                "Action":"",
                "Comment":""
            }
        ],
        "ExtraFields": [
            {
                "Name":"",
                "Value":""
            }
        ]
    }
    return m_data