import os
import json
import sys
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, List

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from flask import json
from loggers.main_logger import get_logger
from clients.mintsoftClient import MintsoftOrderClient
from mappers.main_mapper import map_return
from mappers.client_mapper import map_client
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent   
MODEL_PATH = BASE_DIR / "models" / "5411RMAReturn_Complete.json"

with MODEL_PATH.open("r", encoding="utf-8") as f:
    tb_data = json.load(f)

def fetch_mintsoft_orders(data) -> List[Dict]:
    logger = get_logger("mintsoft_service", "m_service.log")
    logger.info("Starting to fetch Mintsoft orders")
    merchant_name = data[0]["event_data"]["merchant_integration"]["merchant"]["name"]
    client_id = map_client(merchant_name)

    try:
        status_ids = [4, 5, 6]  
        client = MintsoftOrderClient()
        all_orders = []
        for s in status_ids:
            logger.info(f"Fetching orders with status ID: {s}")
            orders = client.get_orders(client_id=client_id, status_id=s)
            logger.info(f"Fetched {len(orders)} orders with status ID {s} from Mintsoft")
            all_orders.extend(orders)
        orders = all_orders
        logger.info(f"Fetched {len(orders)} orders from Mintsoft")
        return orders
    except Exception as e:
        logger.error(f"Error fetching Mintsoft orders: {e}")
        return []
    
def match_rma_order(orders, data):
    logger = get_logger("mintsoft_service", "m_service.log")
    logger.info("Starting to match RMA order with Mintsoft orders")
    rma_order_name = data[0]["event_data"]["line_items"][0]["storefront_order_number"]
    for order in orders:
        if str(order.get("OrderNumber")) == str(rma_order_name):
            logger.info(f"Found matching order in Mintsoft for RMA order name: {rma_order_name}")
            return order.get("ID")
    logger.warning(f"No matching order found in Mintsoft for RMA order name: {rma_order_name}")
    return None

def create_return(data):
    orders = fetch_mintsoft_orders(tb_data)
    order_id = match_rma_order(orders, tb_data)
    if order_id is None:
        logger = get_logger("mintsoft_service", "m_service.log")
        m_return = map_return(data)
        MintsoftOrderClient.create_external_return(m_return)
        return None
    else:
        #create return in mintsoft
        return None