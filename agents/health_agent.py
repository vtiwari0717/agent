"""
Health Agent Module.

Handles all biometrics, metabolic calculations (BMR, TDEE), and 
dynamic nutritional adjustments based on age, BMI, and specific health goals.
"""

import logging
from enum import Enum
from typing import Dict, Union, Any

# Configure module-level logger
logger = logging.getLogger(__name__)

# ---------- ENUMS ----------
class Gender(Enum):
    MALE = "male"
    FEMALE = "female"

class ActivityLevel(Enum):
    SEDENTARY = "sedentary"          # Little or no exercise
    LIGHTLY_ACTIVE = "lightly_active" # Light exercise/sports 1-3 days/week
    MODERATELY_ACTIVE = "moderately_active" # Moderate exercise/sports 3-5 days/week
    VERY_ACTIVE = "very_active"      # Hard exercise/sports 6-7 days/week
    EXTRA_ACTIVE = "extra_active"    # Very hard exercise/sports & physical job

class Goal(Enum):
    WEIGHT_LOSS = "weight_loss"
    MAINTENANCE = "maintenance"
    MUSCLE_GAIN = "muscle_gain"

# ---------- AGENT ----------
class HealthAgent:
    """
    Intelligent agent responsible for calculating health metrics and 
    defining nutritional targets based on complex physiological rules.
    """

    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.HealthAgent")

    # ---------- UTILITIES ----------
    @staticmethod
    def _normalize_enum(value: Union[str, Enum], enum_class: Enum, default: Enum) -> Enum:
        """Helper to safely convert strings to Enums."""
        if isinstance(value, enum_class):
            return value
        try:
            # Clean string: "Weight Loss" -> "weight_loss"
            clean_val = str(value).lower().strip().replace(" ", "_")
            # Handle specific aliases if needed
            if clean_val == "maintain": return Goal.MAINTENANCE
            return enum_class(clean_val)
        except (ValueError, AttributeError):
            logger.warning(f"Invalid {enum_class.__name__}: {value}. Using default: {default.value}")
            return default

    # ---------- CORE CALCULATIONS ----------
    def analyze_user(self, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point. Takes raw user data and returns a full health analysis.
        """
        try:
            # 1. Extract and Normalize Inputs
            weight = float(user_profile.get('weight', 0))
            height = float(user_profile.get('height', 0))
            age = int(user_profile.get('age', 25))
            
            gender = self._normalize_enum(user_profile.get('gender'), Gender, Gender.MALE)
            activity = self._normalize_enum(user_profile.get('activity_level'), ActivityLevel, ActivityLevel.MODERATELY_ACTIVE)
            goal = self._normalize_enum(user_profile.get('goal'), Goal, Goal.MAINTENANCE)

            # 2. Run Calculations
            bmi_data = self.calculate_bmi(weight, height)
            bmr = self.calculate_bmr(weight, height, age, gender)
            tdee = self.calculate_tdee(bmr, activity)
            
            # 3. Calculate Target Calories (Applying Notebook Logic: Age/BMI Rules)
            target_calories = self.calculate_adjusted_calories(
                tdee, goal, age, bmi_data['category']
            )

            # 4. Calculate Macros
            macros = self.calculate_macros(target_calories, goal)

            self.logger.info(f"Analyzed user: BMI={bmi_data['bmi']}, Target={target_calories} kcal")

            return {
                "biometrics": {
                    "bmi": bmi_data['bmi'],
                    "bmi_category": bmi_data['category'],
                    "bmr": bmr,
                    "tdee": tdee
                },
                "targets": {
                    "calories": target_calories,
                    "protein": macros['protein_g'],
                    "carbs": macros['carbs_g'],
                    "fats": macros['fats_g']
                }
            }

        except Exception as e:
            self.logger.error(f"Error in analyze_user: {e}")
            return {}

    def calculate_bmi(self, weight: float, height_cm: float) -> Dict[str, Union[float, str]]:
        """Calculates BMI and returns score + category."""
        if weight <= 0 or height_cm <= 0:
            return {"bmi": 0, "category": "Normal"} # Safe fallback

        height_m = height_cm / 100
        bmi = round(weight / (height_m ** 2), 2)

        if bmi < 18.5: category = "Underweight"
        elif bmi < 25: category = "Normal"
        elif bmi < 30: category = "Overweight"
        else: category = "Obese"

        return {"bmi": bmi, "category": category}

    def calculate_bmr(self, weight: float, height_cm: float, age: int, gender: Gender) -> int:
        """Mifflin-St Jeor Equation."""
        # Formula: 10*W + 6.25*H - 5*A (+5 for men, -161 for women)
        base = (10 * weight) + (6.25 * height_cm) - (5 * age)
        return int(base + 5 if gender == Gender.MALE else base - 161)

    def calculate_tdee(self, bmr: int, activity_level: ActivityLevel) -> int:
        """Calculates Total Daily Energy Expenditure based on activity multiplier."""
        # Multipliers derived from standard nutrition science
        multipliers = {
            ActivityLevel.SEDENTARY: 1.2,
            ActivityLevel.LIGHTLY_ACTIVE: 1.375,
            ActivityLevel.MODERATELY_ACTIVE: 1.55,
            ActivityLevel.VERY_ACTIVE: 1.725,
            ActivityLevel.EXTRA_ACTIVE: 1.9,
        }
        return int(bmr * multipliers[activity_level])

    def calculate_adjusted_calories(self, tdee: int, goal: Goal, age: int, bmi_category: str) -> int:
        """
        Applies complex logic from the Data Science Notebook:
        - Goal Multipliers (0.85 for loss, 1.15 for gain)
        - Age Penalties (>40 years old)
        - BMI Adjustments (Underweight/Obese handling)
        """
        calories = float(tdee)

        # --- 1. Goal Adjustment ---
        if goal == Goal.WEIGHT_LOSS:
            calories *= 0.85  # 15% Deficit
        elif goal == Goal.MUSCLE_GAIN:
            calories *= 1.15  # 15% Surplus
        # Maintenance stays at 1.0

        # --- 2. Age Adjustment (Logic from Notebook) ---
        if age > 40:
            # Metabolism slows down, reduce intake slightly to prevent creep
            calories *= 0.95
        elif 18 <= age <= 25 and goal == Goal.MUSCLE_GAIN:
            # Young adults have higher metabolic adaptability
            calories *= 1.05

        # --- 3. BMI Adjustment (Logic from Notebook) ---
        if bmi_category == "Underweight":
            # If underweight, ensure we aren't restricting, even if goal is maintenance
            calories = max(calories, tdee * 1.1)
        elif bmi_category in ["Overweight", "Obese"] and goal == Goal.WEIGHT_LOSS:
            # If obese, we can handle a slightly larger deficit safely, but we stick to 
            # the notebook's logic of just ensuring we don't overestimate TDEE.
            # We apply a slight 0.9 correction to be conservative.
            calories *= 0.95

        return int(calories)

    def calculate_macros(self, calories: int, goal: Goal) -> Dict[str, int]:
        """
        Calculates macronutrient split (Protein/Carbs/Fats) based on goal.
        Ratios derived from the project notebook analysis.
        """
        if goal == Goal.WEIGHT_LOSS:
            # High Protein (30%), Moderate Carbs (40%), Moderate Fat (30%)
            ratios = (0.30, 0.40, 0.30)
        elif goal == Goal.MUSCLE_GAIN:
            # Moderate Protein (30%), High Carbs (50%) for energy, Low Fat (20%)
            ratios = (0.30, 0.50, 0.20)
        else: # Maintenance
            # Balanced: 25% P, 50% C, 25% F
            ratios = (0.25, 0.50, 0.25)

        p_ratio, c_ratio, f_ratio = ratios

        return {
            "protein_g": int((calories * p_ratio) / 4),
            "carbs_g": int((calories * c_ratio) / 4),
            "fats_g": int((calories * f_ratio) / 9)
        }