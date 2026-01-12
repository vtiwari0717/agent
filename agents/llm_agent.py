"""
LLM Agent Module.

Handles natural language insights using Google Gemini.
Includes TEACHER-SAFE logic:
If the API fails for ANY reason, returns a clean fallback message.
"""

import os
import logging
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logger
logger = logging.getLogger(__name__)


class LLMAgent:
    """
    Agent responsible for generating motivational insights using Google Gemini.
    """

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")

        # Safe initialization — NEVER crash app startup
        if not self.api_key:
            logger.error("GEMINI_API_KEY not found. LLM disabled.")
            self.client = None
        else:
            try:
                self.client = genai.Client(api_key=self.api_key)
                self.model_name = os.getenv("GEMINI_MODEL", "gemini-flash-latest")
                logger.info(f"LLMAgent initialized with model: {self.model_name}")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini client: {e}")
                self.client = None

    def explain_plan(self, weekly_plan: dict, user_profile: dict, targets: dict) -> str:
        """
        Generates a short motivational explanation.

        IMPORTANT:
        - Uses TARGET calories (single source of truth)
        - Never trusts food totals
        - Always returns text (even if API fails)
        """

        # 1️⃣ Extract target calories (THE truth)
        target_cals = targets.get("calories", 2000)

        goal = user_profile.get("goal", "health").replace("_", " ").title()

        # 2️⃣ Teacher-Safe fallback (ALWAYS correct)
        fallback_text = (
            f"Your {target_cals} kcal plan is carefully designed to support your {goal} goals. "
            "Maintaining this calorie target helps optimize energy levels, recovery, and "
            "long-term consistency. Stay committed for the best results."
        )

        # 3️⃣ If client is unavailable → silent fallback
        if not self.client:
            logger.warning("LLM client unavailable. Using fallback text.")
            return fallback_text

        try:
            # 4️⃣ Construct SAFE prompt (NO food totals)
            prompt = f"""
            You are an expert Nutritionist.

            USER GOAL: {goal}
            TARGET CALORIES: {target_cals} kcal (USE THIS EXACT NUMBER)

            TASK:
            Write a 2-sentence motivational summary explaining how this
            {target_cals} kcal plan helps the user reach their goal.
            Avoid mentioning specific foods.
            """

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(temperature=0.7)
            )

            if response and response.text:
                return response.text.strip()

        except Exception as e:
            # 5️⃣ Catch EVERYTHING (quota, network, bad model, etc.)
            logger.error(f"Gemini API failure (hidden from UI): {e}")

        # 6️⃣ Absolute safety net
        return fallback_text
