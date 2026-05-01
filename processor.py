# processor.py

from cost_model import predict_cost
from aiservices import generate_ai


def process_data(data):
    """
    data = {
        "description": str,
        "items": [
            {
                "length": float,
                "width": float,
                "quantity": int,
                "material": str,
                "shape": str,
                "thickness": float
            },
            ...
        ]
    }
    """

    description = data.get("description", "")
    items_input  = data.get("items", [])

    if not items_input:
        return {"error": "No items provided"}, 400

    # ── ML cost prediction per item ──────────────────────
    item_results = []
    grand_total  = 0.0

    for i, item in enumerate(items_input):
        length    = float(item.get("length")    or 0)
        width     = float(item.get("width")     or 0)
        quantity  = int(item.get("quantity")    or 1)
        material  = item.get("material",  "Steel")
        shape     = item.get("shape",     "Flat Bar")
        thickness = float(item.get("thickness") or 0)

        cost_data = predict_cost(length, width, quantity, material, shape, thickness)

        item_cost = cost_data["total_cost"]
        grand_total += item_cost

        item_results.append({
            "name":             f"Item {str(i + 1).zfill(2)}",
            "material":         material,
            "shape":            shape,
            "material_needed":  cost_data["material_needed"],
            "price_per_meter":  cost_data["price_per_meter"],
            "total_cost":       item_cost,
            "time":             f"{round(cost_data['material_needed'] * 0.5, 1)} hrs"
        })

    # ── AI generation for the whole project ─────────────
    ai_data = generate_ai(description, items_input)

    return {
        "items":       item_results,
        "grand_total": grand_total,
        "total_time":  ai_data["time"],
        "steps":       ai_data["steps"],
        "safety":      ai_data["safety"],
        "alternatives":ai_data["alternatives"]
    }