import json

with open("models/mintsoft_return_reasons_model.json", "r") as f:
    return_reasons = json.load(f)    

def map_return_reason(item: dict):
    tb_disposition = item.get("disposition", "Unknown")
    if tb_disposition == "Return to Stock":
        return 1
    elif tb_disposition == "Exception":
        return 2
    elif tb_disposition == "Donate":
        return 3
    elif tb_disposition == "Missing":
        return 6
    else:
        return 5
    


