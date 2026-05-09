# processor.py
# Handles multi-item cost estimation + AI generation

from cost_model import predict_cost
from aiservices import generate_ai
from logger import estimate_logger, error_logger
import time

# ── LIMITS ───────────────────────────────────────────────
MAX_LENGTH    = 100    # metres
MAX_WIDTH     = 100    # metres
MAX_QUANTITY  = 500
MAX_THICKNESS = 100    # mm
MAX_ITEMS     = 20


def process_data(data):
    start_time  = time.time()
    description = data.get("description", "").strip()
    items_input = data.get("items", [])

    estimate_logger.info(
        f"ESTIMATE START | items={len(items_input)} | "
        f"description='{description[:80]}'"
    )

    # ── VALIDATE ITEM COUNT ───────────────────────────────
    if not items_input:
        estimate_logger.warning("ESTIMATE REJECTED | reason=no items provided")
        return {"error": "No items provided."}, 400

    if len(items_input) > MAX_ITEMS:
        estimate_logger.warning(
            f"ESTIMATE REJECTED | reason=too many items | count={len(items_input)}"
        )
        return {"error": f"Maximum {MAX_ITEMS} items allowed per estimate."}, 400

    # ── VALIDATE EACH ITEM ────────────────────────────────
    for i, item in enumerate(items_input):
        num       = i + 1
        length    = float(item.get("length")    or 0)
        width     = float(item.get("width")     or 0)
        quantity  = int(item.get("quantity")    or 0)
        thickness = float(item.get("thickness") or 0)

        if length <= 0 or width <= 0:
            estimate_logger.warning(
                f"ESTIMATE REJECTED | item={num} | reason=zero dimensions | "
                f"length={length} | width={width}"
            )
            return {"error": f"Item {num}: Length and width must be greater than 0."}, 400

        if length > MAX_LENGTH:
            estimate_logger.warning(
                f"ESTIMATE REJECTED | item={num} | reason=length over limit | length={length}"
            )
            return {"error": f"Item {num}: Length {length}m exceeds maximum of {MAX_LENGTH}m."}, 400

        if width > MAX_WIDTH:
            estimate_logger.warning(
                f"ESTIMATE REJECTED | item={num} | reason=width over limit | width={width}"
            )
            return {"error": f"Item {num}: Width {width}m exceeds maximum of {MAX_WIDTH}m."}, 400

        if quantity <= 0:
            estimate_logger.warning(
                f"ESTIMATE REJECTED | item={num} | reason=invalid quantity | qty={quantity}"
            )
            return {"error": f"Item {num}: Quantity must be at least 1."}, 400

        if quantity > MAX_QUANTITY:
            estimate_logger.warning(
                f"ESTIMATE REJECTED | item={num} | reason=quantity over limit | qty={quantity}"
            )
            return {"error": f"Item {num}: Quantity {quantity} exceeds maximum of {MAX_QUANTITY}."}, 400

        if thickness > MAX_THICKNESS:
            estimate_logger.warning(
                f"ESTIMATE REJECTED | item={num} | reason=thickness over limit | thickness={thickness}"
            )
            return {"error": f"Item {num}: Thickness {thickness}mm exceeds maximum of {MAX_THICKNESS}mm."}, 400

    # ── COST MODEL PER ITEM ───────────────────────────────
    item_results = []
    grand_total  = 0.0

    for i, item in enumerate(items_input):
        num       = i + 1
        length    = float(item.get("length")    or 0)
        width     = float(item.get("width")     or 0)
        quantity  = int(item.get("quantity")    or 1)
        material  = item.get("material",  "Steel")
        shape     = item.get("shape",     "Flat Bar")
        thickness = float(item.get("thickness") or 0)

        try:
            cost_data = predict_cost(length, width, quantity, material, shape, thickness)
            item_cost = cost_data["total_cost"]
            grand_total += item_cost

            item_results.append({
                "name":            f"Item {str(num).zfill(2)}",
                "material":        material,
                "shape":           shape,
                "material_needed": cost_data["material_needed"],
                "price_per_meter": cost_data["price_per_meter"],
                "total_cost":      item_cost,
                "time":            f"{round(cost_data['material_needed'] * 0.5, 1)} hrs"
            })

            estimate_logger.info(
                f"ITEM COSTED | item={num} | material={material} | shape={shape} | "
                f"length={length}m | width={width}m | qty={quantity} | "
                f"needed={cost_data['material_needed']:.2f}m | "
                f"price_per_m=R{cost_data['price_per_meter']:.2f} | "
                f"total=R{item_cost:.2f}"
            )

        except Exception as e:
            error_logger.error(
                f"COST MODEL ERROR | item={num} | material={material} | "
                f"shape={shape} | error={str(e)}",
                exc_info=True
            )
            return {"error": f"Cost model failed on item {num}. Please check your inputs."}, 500

    # ── AI GENERATION ─────────────────────────────────────
    ai_data = generate_ai(description, items_input)

    # ── DONE ──────────────────────────────────────────────
    elapsed = round(time.time() - start_time, 2)
    estimate_logger.info(
        f"ESTIMATE COMPLETE | items={len(items_input)} | "
        f"grand_total=R{grand_total:.2f} | duration={elapsed}s"
    )

    return {
        "items":        item_results,
        "grand_total":  grand_total,
        "total_time":   ai_data["time"],
        "steps":        ai_data["steps"],
        "safety":       ai_data["safety"],
        "alternatives": ai_data["alternatives"]
    }