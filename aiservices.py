# aiservices.py

from openai import OpenAI
from dotenv import load_dotenv
import os
import json

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
print("Loaded API KEY:", api_key)

if not api_key:
    raise ValueError("OPENAI_API_KEY not found. Check your .env file.")

client = OpenAI(api_key=api_key)


def generate_ai(description, items):
    """
    Generate AI welding plan for multiple metal items.
    items = list of dicts with keys: material, shape, length, width, quantity, thickness
    """

    items_summary = "\n".join([
        f"  - Item {i+1}: {item['material']} {item['shape']}, "
        f"{item['length']}m x {item['width']}m, qty {item['quantity']}, "
        f"thickness {item['thickness']}mm"
        for i, item in enumerate(items)
    ])

    prompt = f"""
You are a welding expert assistant.

Project description: {description}

The welder needs to fabricate {len(items)} metal item(s):
{items_summary}

Return ONLY valid JSON with no extra text, no markdown, no code blocks:
{{
  "time": "total estimated time for all items combined",
  "steps": ["step1", "step2", "step3", "step4", "step5"],
  "safety": ["rule1", "rule2", "rule3", "rule4"],
  "alternatives": ["alt1", "alt2", "alt3"]
}}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        content = response.choices[0].message.content.strip()

        # Strip markdown fences if present
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        content = content.strip()

        return json.loads(content)

    except Exception as e:
        print("AI ERROR:", e)

        return {
            "time": f"{len(items) * 2}-{len(items) * 4} hours (estimated)",
            "steps": [
                "Measure and mark all cut lines on each piece",
                "Cut all metal items to required dimensions",
                "Deburr and grind all cut edges smooth",
                "Tack weld frames and joints into position",
                "Full weld all joints and inspect seams",
                "Grind welds flush and clean surfaces",
                "Apply primer and paint or powder coat"
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
                "Consider powder coating instead of paint for longevity",
                "Add corner gussets to improve joint reinforcement",
                "Use stainless steel for outdoor or high-moisture environments"
            ]
        }