# 🧠 MacroMind AI — Intelligent Diet Planning System

## 🚀 Overview

**MacroMind AI** is an advanced **Agentic AI-powered Diet Planning System** designed to generate **hyper-personalized weekly meal plans**.  
Unlike basic calorie trackers, the system uses a **multi-agent architecture** to combine metabolic science, intelligent food pairing, and large language models to deliver realistic and culturally coherent nutrition plans.

The application calculates precise metabolic needs, curates meals from a dataset of **10,000+ food items**, and provides AI-powered insights to help users stay consistent with their health goals.

---

## 🔗 Live Demo
👉 **[Launch the App](https://ai-personalized-diet-planner.streamlit.app/)**  
*(If the app is asleep, click “Wake App” and wait a few seconds.)*

---

## 🏗️ System Architecture — Multi-Agent Design

MacroMind AI follows a modular agent-based architecture where each agent has a clearly defined role.

### 🧮 Health Agent — The Calculator
- Analyzes user biometrics (age, height, weight, gender, activity level)
- Uses the **Mifflin-St Jeor Equation**
- Calculates **BMR, TDEE**, and daily macro targets

### 🥗 Nutrition Agent — The Chef
- Selects meals from a **10,000+ food database**
- Applies **smart food pairing logic**
- Fills calorie gaps to stay close to daily targets
- Enforces strict **Veg / Non-Veg separation**

### 🧠 Cognitive Agent — The Coach
- Powered by **Google Gemini**
- Analyzes the generated plan
- Produces a motivational and goal-aligned explanation

### ⚙️ Recommendation Engine — The Orchestrator
- Coordinates all agents
- Ensures seamless data flow between calculations, meal generation, and AI explanation

---

## ✨ Key Features
- Dynamic Streamlit dashboard
- Interactive Plotly-based analytics
- Extensive multi-cuisine food database
- AI-generated plan explanations
- Modular and scalable agentic design

---

## 🛠️ Tech Stack
- **Frontend:** Streamlit, Custom CSS
- **Backend:** Python 3.10+
- **Data Processing:** Pandas, NumPy
- **AI / LLM:** Google GenAI SDK (Gemini)
- **Visualization:** Plotly

---

## 📂 Project Structure

---

## 📂 Project Structure
```text
├── agents/
│   ├── health_agent.py        # Metabolic calculations
│   ├── nutrition_agent.py     # Food selection & logic
│   └── llm_agent.py           # Google Gemini integration
├── services/
│   └── recommendation_engine.py # Main orchestration layer
├── data/
│   └── expanded_food_dataset_10000.csv # Food database
├── app.py                     # Main Streamlit UI
├── requirements.txt           # Dependencies
└── .env                       # API Keys (Not shared)
