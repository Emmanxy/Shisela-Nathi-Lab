# aiservices.py
# OpenAI GPT integration for welding project AI generation

from openai import OpenAI
from dotenv import load_dotenv
from logger import estimate_logger, error_logger
import os
import json
import time

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    error_logger.error("STARTUP ERROR | OPENAI_API_KEY not found in .env file")
    raise ValueError("OPENAI_API_KEY not found. Check your .env file.")

estimate_logger.info("OpenAI client initialised successfully")
client = OpenAI(api_key=api_key)


# ── WELDING RELEVANCE CHECK ───────────────────────────────
WELDING_KEYWORDS = [
    "metal", "steel", "iron", "weld", "frame", "gate", "pipe",
    "bar", "tube", "fence", "door", "window", "bracket", "rack",
    "stand", "table", "chair", "roof", "structure", "fabricat",
    "grille", "railing", "staircase", "beam", "angle", "sheet",
    "alumin", "stainless", "mild", "section", "hollow"
]

def is_welding_relevant(description):
    """Returns False if description exists but has no welding-related terms."""
    if not description:
        return True  # empty description is allowed — items carry the context
    return any(k in description.lower() for k in WELDING_KEYWORDS)


# ── FALLBACK RESPONSE ────────────────────────────────────
def fallback_response(items):
    count = len(items)
    return {
        "time": f"{count * 2}–{count * 4} hours (estimated)",
        "steps": [
            "Measure and mark all cut lines on each piece",
            "Cut all metal items to required dimensions",
            "Deburr and grind all cut edges smooth",
            "Tack weld frames and joints into position",
            "Full weld all joints and inspect seams",
            "Grind welds flush and clean all surfaces",
            "Apply primer then paint or powder coat"
        ],
        "safety": [
            "Always wear a welding helmet and gloves",
            "Ensure proper ventilation to avoid fume inhalation",
            "Keep a fire extinguisher nearby at all times",
            "Wear steel-toe boots and long-sleeve protective clothing",
            "Secure all workpieces with clamps before cutting or welding"
        ],
        "alternatives": [
            "Use heavier gauge material for extra structural strength",
            "Consider powder coating instead of paint for longer durability",
            "Add corner gussets to improve joint reinforcement",
            "Use stainless steel for outdoor or high-moisture environments"
        ]
    }


# ── MAIN AI FUNCTION ─────────────────────────────────────
def generate_ai(description, items):
    """
    Generate AI welding plan for one or more metal items.
    Logs every call, success, fallback, and failure.
    """

    estimate_logger.info(
        f"AI REQUEST | items={len(items)} | "
        f"description='{description[:80] if description else 'none'}'"
    )

    # Check if description is welding-related
    if not is_welding_relevant(description):
        estimate_logger.warning(
            f"AI REJECTED | reason=non-welding description | "
            f"description='{description[:80]}'"
        )
        return {
            "time": "N/A",
            "steps": [
                "Project description does not appear to be metal or welding related. "
                "Please describe a fabrication project (e.g. window frame, security gate, steel rack)."
            ],
            "safety": ["Please re-enter a valid welding project description."],
            "alternatives": [
                "Try: 'bedroom window frame'",
                "Try: 'security gate using square tube'",
                "Try: 'steel staircase railing'"
            ]
        }

    # Build items summary for the prompt
    items_summary = "\n".join([
        f"  - Item {i+1}: {item.get('material','Steel')} {item.get('shape','Flat Bar')}, "
        f"{item.get('length',0)}m x {item.get('width',0)}m, "
        f"qty {item.get('quantity',1)}, thickness {item.get('thickness',0)}mm"
        for i, item in enumerate(items)
    ])

    prompt = f"""You are a welding and metal fabrication expert.

Project description: {description if description else "General welding project"}

The welder needs to fabricate {len(items)} metal item(s):
{items_summary}

Return ONLY valid JSON — no markdown, no code blocks, no extra text:
{{
  "time": "total estimated time for all items combined",
  "steps": ["step1", "step2", "step3", "step4", "step5", "step6"],
  "safety": ["rule1", "rule2", "rule3", "rule4"],
  "alternatives": ["alt1", "alt2", "alt3"]
}}"""

    start = time.time()

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=800
        )

        content = response.choices[0].message.content.strip()

        # Strip markdown fences if GPT adds them
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        content = content.strip()

        result  = json.loads(content)
        elapsed = round(time.time() - start, 2)

        estimate_logger.info(
            f"AI SUCCESS | duration={elapsed}s | "
            f"steps={len(result.get('steps', []))} | "
            f"time_estimate='{result.get('time', 'N/A')}'"
        )

        return result

    except json.JSONDecodeError as e:
        elapsed = round(time.time() - start, 2)
        error_logger.error(
            f"AI JSON PARSE ERROR | duration={elapsed}s | error={str(e)} | "
            f"raw_content={content[:200] if 'content' in dir() else 'N/A'}"
        )
        estimate_logger.warning("AI FALLBACK USED | reason=JSON parse error")
        return fallback_response(items)

    except Exception as e:
        elapsed = round(time.time() - start, 2)
        error_logger.error(
            f"AI FAILURE | duration={elapsed}s | error={str(e)}",
            exc_info=True
        )
        estimate_logger.warning(f"AI FALLBACK USED | reason=API error | error={str(e)}")
        return fallback_response(items)