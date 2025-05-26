import re
import json
import ast
import os
from flask import Flask, request, jsonify, render_template
from openai import OpenAI
from dotenv import load_dotenv

app = Flask(__name__)
load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

# Brand-specific mod brands
mod_brands = {
    "BMW": ["Dinan", "AC Schnitzer", "Manhart"],
    "Mercedes": ["RENNtech", "Weistec", "Brabus"],
    "Audi": ["ABT Sportsline", "APR", "Unitronic"],
    "Porsche": ["TechArt", "RUF", "Dundon"],
    "Ferrari": ["Novitec", "Capristo"],
    "Lamborghini": ["Underground Racing", "VF Engineering"]
}

@app.route('/')
def home():
    return render_template('index.html')

def extract_car_info(description):
    prompt = f"""
Extract the following details from this car description: "{description}"

Return JSON like:
{{
  "year": "...",
  "make": "...",
  "model": "...",
  "transmission": "...",
  "drivetrain": "...",
  "body": "..."
}}

If something is missing, use an empty string. Return only valid JSON.
"""
    try:
        response = client.chat.completions.create(
            model="anthropic/claude-3-haiku",
            messages=[
                {"role": "system", "content": "You're an automotive AI that extracts clean JSON car info."},
                {"role": "user", "content": prompt}
            ]
        )
        output = response.choices[0].message.content.strip()
        return json.loads(output) if output.startswith("{") else ast.literal_eval(output)
    except Exception as e:
        print("PARSE ERROR:", e)
        return {}

def get_specs_and_mods(clean_input, brand):
    tuning_brands = ", ".join(mod_brands.get(brand, []))

    prompt = f"""
You're an expert car performance tuner in Canada.

Specs for: "{clean_input}"

Show:
1. Accurate **factory specs**
2. Estimated **Stage 1** and **Stage 2** mods
3. **Realistic** brands and results (especially HP, torque, 0–100)
4. List parts with price and brand: intake, downpipe, exhaust, intercooler, TCU, flex fuel

Format:
**Specs**
Model: ...
Horsepower: ...
Torque: ...
0–100 km/h: ...
Quarter Mile: ...
Engine: ...
Drivetrain: ...
Transmission: ...
Fuel Economy: ...
Price: ...
Reliability: ...

**Stage 1 Tune**
+HP / +lb-ft → New totals
New 0–100 km/h
Brands: {tuning_brands}
Price: $ CAD

**Stage 2 Tune**
Same structure.

**Other Mods**
- Intake (Brand, Price)
- Downpipe (Brand, Price)
- Exhaust (Brand, Price)
- Intercooler (Brand, Price)
- TCU Tune (Price)
- Flex Fuel (Price)

Close with: "Would you like to mod for power, sound, or both?"

Respond in plain readable text. DO NOT guess if you're unsure.
"""
    try:
        response = client.chat.completions.create(
            model="anthropic/claude-3-haiku",
            messages=[
                {"role": "system", "content": "You're a tuning expert. Be accurate and only list known mods."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("MOD ERROR:", e)
        return "❌ Sorry, I couldn’t fetch tuning info."

@app.route('/compare', methods=['POST'])
def compare():
    try:
        user_input = request.json.get("description", "").strip()
        car_info = extract_car_info(user_input)

        missing = [k for k, v in car_info.items() if not v]
        if missing:
            return jsonify({
                "follow_up": True,
                "questions": [f"Please provide the car’s {field}." for field in missing]
            })

        cleaned = f"{car_info['year']} {car_info['make']} {car_info['model']} {car_info['transmission']} {car_info['drivetrain']} {car_info['body']}"
        result = get_specs_and_mods(cleaned, car_info['make'])

        return jsonify({ "result": result })

    except Exception as e:
        print("ERROR:", e)
        return jsonify({ "error": f"⚠️ {str(e)}" })

if __name__ == '__main__':
    app.run(debug=True)
