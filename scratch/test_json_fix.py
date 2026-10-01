import re
import json

raw_json = r'''[
  {
    "question_number": 1,
    "steps": [
      {"step": 1, "title": "Reaksi", "explanation": "Persamaan termokimia: $2\\text{NO}_2(g) \\rightleftharpoons \\text{N}_2\\text{O}_4(g)$ dengan $\\Delta H = -57,20\\text{ kJ}$."}
    ]
  }
]'''

def safe_parse_json(text):
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)
    
    try:
        return json.loads(text, strict=False)
    except json.JSONDecodeError:
        pass
    
    # Replace backslash not followed by "
    fixed = re.sub(r'\\(?!")', r'\\\\', text)
    return json.loads(fixed, strict=False)

parsed = safe_parse_json(raw_json)
print("Successfully parsed!", len(parsed))
print("Explanation:", parsed[0]["steps"][0]["explanation"])
