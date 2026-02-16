import os
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from loggers.main_logger import get_logger
from clients.mintsoftClient import MintsoftOrderClient
from mappers.main_mapper import map_return
from mappers.mintsoft_mapper import map_client


class MintsoftReturnService:
    def __init__(self, logger_name: str = "mintsoft_service", log_file: str = "m_service.log"):
        self.logger = get_logger(logger_name, log_file)
        self.client = MintsoftOrderClient()
        self.status_ids = [4, 5, 6]

    def _get_merchant_name(self, data) -> str:
        return data[0]["event_data"]["merchant_integration"]["merchant"]["name"]

    def _get_storefront_order_number(self, data) -> str:
        return data[0]["event_data"]["line_items"][0]["storefront_order_number"]

    def fetch_mintsoft_orders(self, data) -> List[Dict]:
        self.logger.info("Starting to fetch Mintsoft orders")

        merchant_name = self._get_merchant_name(data)
        client_id = map_client(merchant_name)

        all_orders: List[Dict] = []
        try:
            for status_id in self.status_ids:
                self.logger.info(f"Fetching orders with status ID: {status_id}")
                orders = self.client.get_orders(client_id=client_id, status_id=status_id)
                self.logger.info(f"Fetched {len(orders)} orders with status ID {status_id} from Mintsoft")
                all_orders.extend(orders)

            self.logger.info(f"Fetched {len(all_orders)} orders from Mintsoft (total)")
            return all_orders

        except Exception as e:
            self.logger.error(f"Error fetching Mintsoft orders: {e}", exc_info=True)
            return []

    def match_rma_order(self, orders: List[Dict], data) -> Optional[int]:
        self.logger.info("Starting to match RMA order with Mintsoft orders")

        rma_order_name = self._get_storefront_order_number(data)

        for order in orders:
            if str(order.get("OrderNumber")) == str(rma_order_name):
                self.logger.info(f"Found matching order in Mintsoft for RMA order name: {rma_order_name}")
                return order.get("ID")

        self.logger.warning(f"No matching order found in Mintsoft for RMA order name: {rma_order_name}")
        return None

    def create_return(self, data) -> Optional[int]:
        orders = self.fetch_mintsoft_orders(data)
        order_id = self.match_rma_order(orders, data)

        m_return = map_return(data)

        try:
            if order_id is None:
                self.logger.info("Order not found in Mintsoft. Creating EXTERNAL return.")
                print(m_return)
                response = self.client.create_external_return(data=m_return)
                self.logger.info(f"External return created. Response: {response}")
                return None

            self.logger.info(f"Order found (ID={order_id}). Creating standard return.")
            return_id = self.client.create_return(
                order_id=order_id,
                warehouse_id=m_return["WarehouseId"],
                client_id=m_return.get("ClientId"),  # safe if key exists
            )
            self.logger.info(f"Created return with ID: {return_id}")
            return return_id

        except Exception as e:
            self.logger.error(f"Error creating return: {e}", exc_info=True)
            return None


if __name__ == "__main__":
    from pathlib import Path
    import json

    BASE_DIR = Path(__file__).resolve().parent.parent
    MODEL_PATH = BASE_DIR / "models" / "tb_rma_model.json"

    with MODEL_PATH.open("r", encoding="utf-8") as f:
        tb_data = json.load(f)

    service = MintsoftReturnService()
    service.create_return(tb_data)
