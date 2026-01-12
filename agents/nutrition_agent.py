import pandas as pd
import os
import logging
import re
import json
from typing import Dict, List, Any

# --------------------------------------------------
# LOGGING CONFIGURATION
# --------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NutritionAgent:
    """
    Nutrition Agent for generating realistic, culturally coherent meal plans.
    Implements 'Defense in Depth' to strictly enforce Veg / Non-Veg selection.
    """

    def __init__(self, csv_path: str = "expanded_food_dataset_10000.csv"):
        self.csv_path = csv_path
        self.df = None

        # Comprehensive Non-veg keywords for failsafe checks
        self.non_veg_keywords = [
            "chicken", "fish", "egg", "mutton", "gosht", "biryani",
            "omelette", "scrambled", "prawn", "beef", "pork", 
            "lamb", "meat", "bacon", "salami", "duck"
        ]

        # Realistic food pairing logic
        self.pairing_rules = {
            "curry": ["rice", "flatbread", "dry_veg"],
            "dry_veg": ["flatbread", "rice", "curry"],
            "rice": ["curry", "dry_veg", "snack"],
            "soup": ["flatbread", "salad", "breakfast_item"],
            "pasta": ["salad", "soup"],
            "breakfast_item": ["beverage", "fruit"],
            "oats": ["fruit", "beverage", "snack"],
            "flatbread": ["curry", "dry_veg"],
        }

        self._load_data()

    # --------------------------------------------------
    # DATA LOADING & STANDARDIZATION
    # --------------------------------------------------
    def _load_data(self):
        if not os.path.exists(self.csv_path):
            raise FileNotFoundError(f"Dataset not found: {self.csv_path}")

        df = pd.read_csv(self.csv_path)
        df.columns = df.columns.str.strip().str.lower()

        # Standardize column names to match internal logic
        df.rename(columns={
            "food_item": "name",
            "diet": "diet",
            "meal": "meal_time",
            "category": "category",
            "calories": "calories",
            "protein_g": "protein",
            "carbs_g": "carbs",
            "fat_g": "fats"
        }, inplace=True)

        # Clean text fields for reliable matching
        for col in ["name", "diet", "meal_time", "category"]:
            df[col] = df[col].astype(str).str.lower().str.strip()

        self.df = df
        logger.info(f"Nutrition dataset loaded successfully: {len(self.df)} rows")

    # --------------------------------------------------
    # DIET SAFETY CHECK (Layer 2: Whole-Word Regex)
    # --------------------------------------------------
    def _is_diet_safe(self, food_name: str, diet_pref: str) -> bool:
        """
        Uses Regex to ensure keywords match whole words only.
        This prevents 'egg' from blocking 'veggie' or 'eggplant'.
        """
        if diet_pref == "veg":
            # Remove special characters and split into words
            clean_name = re.sub(r'[^a-z\s]', ' ', food_name.lower())
            words = set(clean_name.split())
            
            # Check for exact matches against forbidden keywords
            for keyword in self.non_veg_keywords:
                if keyword in words:
                    return False
        return True

    # --------------------------------------------------
    # PUBLIC API: RECOMMEND MEAL PLAN
    # --------------------------------------------------
    def recommend_meal_plan(self, diet_preference: str, total_calories: float) -> Dict[str, Any]:
        diet_pref = diet_preference.lower().strip()

        # Layer 1: Strict filter based on the CSV 'diet' column
        diet_df = self.df[self.df["diet"] == diet_pref].copy()

        if diet_df.empty:
            return {"error": f"No food items found for diet: {diet_preference}"}

        splits = {
            "Breakfast": 0.25,
            "Lunch": 0.40,
            "Dinner": 0.35
        }

        meal_plan = {}
        for meal_name, ratio in splits.items():
            target = total_calories * ratio

            # Filter by meal time (Breakfast/Lunch/Dinner)
            time_df = diet_df[diet_df["meal_time"] == meal_name.lower()]
            
            # Fallback if specific meal time is empty (though unlikely with 10k rows)
            if time_df.empty:
                time_df = diet_df 

            meal_plan[meal_name] = self._build_meal(time_df, target, diet_pref)

        return meal_plan

    # --------------------------------------------------
    # CORE LOGIC: MEAL BUILDER
    # --------------------------------------------------
    def _build_meal(self, df: pd.DataFrame, target_calories: float, diet_pref: str) -> Dict[str, Any]:
        selected_items = []
        current_cals = 0

        # --- STEP 1: Select Main Item ---
        # Apply Layer 2 Safety Check before sampling
        main_candidates = df[
            df["name"].apply(lambda x: self._is_diet_safe(x, diet_pref))
        ]

        if main_candidates.empty:
            return {"items": [], "total_calories": 0, "warning": "No safe items found"}

        main_item = main_candidates.sample(1).iloc[0]
        selected_items.append(self._format_item(main_item, "Main"))
        current_cals += main_item["calories"]

        # --- STEP 2: Select Side Item ---
        remaining = target_calories - current_cals
        main_cat = main_item["category"]
        compatible_categories = self.pairing_rules.get(main_cat, [])

        if remaining > 50 and compatible_categories:
            side_df = df[
                (df["category"].isin(compatible_categories)) &
                (df["name"] != main_item["name"]) &
                (df["name"].apply(lambda x: self._is_diet_safe(x, diet_pref)))
            ].copy()

            if not side_df.empty:
                # Find side item closest to remaining calorie target
                side_df["diff"] = (side_df["calories"] - remaining).abs()
                side_item = side_df.sort_values("diff").head(5).sample(1).iloc[0]
                selected_items.append(self._format_item(side_item, "Side"))
                current_cals += side_item["calories"]

        return {
            "items": selected_items,
            "total_calories": int(current_cals),
            "macro_summary": self._sum_macros(selected_items)
        }

    # --------------------------------------------------
    # HELPERS: FORMATTING & CALCULATIONS
    # --------------------------------------------------
    def _format_item(self, item: pd.Series, role: str) -> Dict[str, Any]:
        return {
            "name": item["name"].title(),
            "role": role,
            "category": item["category"].title(),
            "calories": int(item["calories"]),
            "protein": float(item["protein"]),
            "carbs": float(item["carbs"]),
            "fats": float(item["fats"])
        }

    def _sum_macros(self, items: List[Dict[str, Any]]) -> Dict[str, float]:
        return {
            "protein": round(sum(i["protein"] for i in items), 2),
            "carbs": round(sum(i["carbs"] for i in items), 2),
            "fats": round(sum(i["fats"] for i in items), 2)
        }

# --------------------------------------------------
# EXECUTION BLOCK (Test Run)
# --------------------------------------------------
if __name__ == "__main__":
    # Initialize the agent
    agent = NutritionAgent("expanded_food_dataset_10000.csv")
    
    # Generate a sample plan
    user_diet = "veg"
    user_calories = 2000
    
    plan = agent.recommend_meal_plan(user_diet, user_calories)
    
    # Output result as clean JSON
    print(f"\n--- {user_diet.upper()} Meal Plan ({user_calories} kcal) ---")
    print(json.dumps(plan, indent=4))