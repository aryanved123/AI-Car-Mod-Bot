# 🚘 AI-Car-Mod-Bot

**AI-Car-Mod-Bot** is a powerful AI chatbot that helps you find performance upgrades for your car and estimates the results of those modifications — including new horsepower, torque, 0–100 km/h, and quarter-mile times.

---

## 💡 What It Can Do

- 🔍 Identify car specs (engine, drivetrain, fuel economy, reliability, etc.)
- 🚀 Suggest real-world mods (Stage 1, Stage 2, intake, downpipe, ECU/TCU tunes, etc.)
- 📊 Show new performance stats *after* tuning
- 🛠 Use brand-specific tuning companies (e.g., ABT for Audi, RENNtech for AMG, Dinan for BMW)
- 🤖 Ask follow-up questions if your input is too vague
- 💬 Designed for Canadian units (L/100km, CAD currency, km/h)

---

## ⚙️ How to Run Locally

```bash
# 1. Clone the repository
git clone https://github.com/aryanved123/AI-Car-Mod-Bot.git

# 2. Enter the project directory
cd AI-Car-Mod-Bot

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add your Groq API key in a .env file (create this in the project root):
# Example .env:
GROQ_API_KEY=gsk_your_real_api_key_here

# 5. Run the Flask app
cd car-chatbot
python app.py
