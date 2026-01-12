"""
Recommendation Engine Service.

This is the main orchestration layer that connects:
1. Health Agent (Calculations)
2. Nutrition Agent (Meal Selection & Smart Pairing)
3. LLM Agent (AI Explanation)
"""

import logging
from typing import Dict, Any

# Import your agents
from agents import HealthAgent, NutritionAgent, LLMAgent

# Configure logger
logger = logging.getLogger(__name__)


class RecommendationEngine:
    """
    Orchestrator for generating personalized diet plans.
    """

    def __init__(self):
        """
        Initialize all agents.
        CRITICAL: Ensures the dataset path matches your folder structure.
        """
        try:
            self.health_agent = HealthAgent()

            # This path MUST match where you put the CSV file
            self.nutrition_agent = NutritionAgent(
                csv_path="data/expanded_food_dataset_10000.csv"
            )

            self.llm_agent = LLMAgent()

            logger.info("RecommendationEngine initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize RecommendationEngine: {e}")
            raise

    def generate_plan(self, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates a complete 7-day diet plan based on user profile.

        Args:
            user_profile (dict): User data (age, weight, height, goal, etc.)

        Returns:
            dict: The final plan including biometrics, meals, and AI explanation.
        """
        logger.info(f"Generating plan for user: {user_profile.get('name', 'User')}")

        try:
            # ---------------------------------------------------------
            # STEP 1: Health Analysis (The Calculator)
            # ---------------------------------------------------------
            health_analysis = self.health_agent.analyze_user(user_profile)

            if not health_analysis:
                return {"error": "Could not analyze health metrics. Check input data."}

            targets = health_analysis["targets"]
            target_calories = targets["calories"]
            diet_pref = user_profile.get("diet_preference", "Veg")

            # ---------------------------------------------------------
            # STEP 2: Generate 7-Day Meal Plan (The Chef)
            # ---------------------------------------------------------
            weekly_plan = {}

            for day in range(1, 8):
                day_label = f"Day {day}"

                daily_meals = self.nutrition_agent.recommend_meal_plan(
                    diet_preference=diet_pref,
                    total_calories=target_calories
                )

                if "error" in daily_meals:
                    return {"error": daily_meals["error"]}

                weekly_plan[day_label] = {
                    "meals": daily_meals,
                    "calories": sum(
                        meal["total_calories"] for meal in daily_meals.values()
                    ),
                    "macros": self._aggregate_daily_macros(daily_meals)
                }

            # ---------------------------------------------------------
            # STEP 3: Generate AI Explanation (The Coach)
            # ---------------------------------------------------------
            # IMPORTANT: Pass `targets` so the LLM sees the REAL calorie goal
            ai_explanation = self.llm_agent.explain_plan(
                weekly_plan,
                user_profile,
                targets
            )

            # ---------------------------------------------------------
            # STEP 4: Construct Final Response
            # ---------------------------------------------------------
            final_plan = {
                "user_profile": user_profile,
                "biometrics": health_analysis["biometrics"],
                "nutritional_targets": targets,
                "weekly_plan": weekly_plan,
                "ai_insight": ai_explanation
            }

            logger.info("Plan generated successfully.")
            return final_plan

        except Exception as e:
            logger.error(f"Error in generate_plan: {e}")
            return {"error": "An unexpected error occurred while generating your plan."}

    def _aggregate_daily_macros(self, daily_meals: Dict) -> Dict[str, float]:
        """
        Helper to sum up protein/carbs/fats for the whole day.
        """
        total_p = 0
        total_c = 0
        total_f = 0

        for meal in daily_meals.values():
            macros = meal.get("macro_summary", {})
            total_p += macros.get("protein", 0)
            total_c += macros.get("carbs", 0)
            total_f += macros.get("fats", 0)

        return {
            "protein": round(total_p, 1),
            "carbs": round(total_c, 1),
            "fats": round(total_f, 1)
        }
