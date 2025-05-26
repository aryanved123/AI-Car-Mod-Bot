import re
import json
import ast
from flask import Flask, request, jsonify, render_template
from openai import OpenAI
import os
from dotenv import load_dotenv

app = Flask(__name__)


load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
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

Return this JSON:
{{
  "year": "...",
  "make": "...",
  "model": "...",
  "transmission": "...",
  "drivetrain": "...",
  "body": "..."
}}

If something is missing, leave it as an empty string.
Respond with ONLY valid JSON.
"""
    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": "You extract car info and return clean JSON."},
                {"role": "user", "content": prompt}
            ]
        )
        raw = response.choices[0].message.content.strip()
        return json.loads(raw) if raw.startswith("{") else ast.literal_eval(raw)
    except Exception as e:
        print("PARSE ERROR:", e)
        return {}

def get_specs_and_mods(cleaned_input, brand):
    tuning_brands = ", ".join(mod_brands.get(brand, []))

    prompt = f"""
You're a car performance specialist.

Give full specs for this car: "{cleaned_input}"
Then list real-world mods. Format like this:

**Specs**
Model: 2021 BMW M5 Competition
Horsepower: 617 HP
Torque: 553 lb-ft
0–100 km/h: 3.1s
Quarter Mile: 11.0s
Engine: 4.4L Twin-Turbo V8
Drivetrain: AWD
Transmission: 8-Speed Auto
Fuel Economy: 13.6 city / 9.9 hwy L/100km
Price: $123,000 CAD
Reliability: 8.5/10

**Stage 1 Tune**
+50 HP, +60 lb-ft → 667 HP, 613 lb-ft
New 0–100: 2.9s
Brands: {tuning_brands}
Price: $1,500 CAD

**Stage 2 Tune**
+90 HP, +100 lb-ft → 707 HP, 653 lb-ft
New 0–100: 2.7s
Brands: {tuning_brands}
Price: $2,500 CAD

**Other Mods**
- Intake: Eventuri ($1,000 CAD)
- Downpipe: CTS Turbo ($1,500 CAD)
- Exhaust: Akrapovic ($3,000 CAD)
- Intercooler: Wagner ($2,000 CAD)
- TCU Tune: $1,200 CAD
- Flex Fuel Kit: $1,300 CAD

End with: "Would you like to mod for power, sound, or both?"
Only reply with clear readable text.
"""
    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": "You respond like a car performance consultant."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("MOD ERROR:", e)
        return "Sorry, I couldn’t fetch tuning info."

@app.route('/compare', methods=['POST'])
def compare():
    try:
        user_input = request.json.get("description", "").strip()
        car_info = extract_car_info(user_input)

        # Ask for missing info
        missing = [k for k, v in car_info.items() if not v]
        if missing:
            return jsonify({
                "follow_up": True,
                "questions": [f"Please provide the car's {field}." for field in missing]
            })

        # Build cleaned string
        cleaned = f"{car_info['year']} {car_info['make']} {car_info['model']} {car_info['transmission']} {car_info['drivetrain']} {car_info['body']}"
        result = get_specs_and_mods(cleaned, car_info['make'])

        return jsonify({"result": result})

    except Exception as e:
        print("ERROR:", e)
        return jsonify({"error": f"⚠️ {str(e)}"})

if __name__ == '__main__':
    app.run(debug=True)
