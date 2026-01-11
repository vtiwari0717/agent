"""
Nutrition Agent Module.

Responsible for generating realistic, culturally coherent meal combinations
(e.g., Dal + Rice, Soup + Bread) while adhering to strict caloric targets.
"""

import pandas as pd
import os
import random
import logging
import re
from typing import Dict, List, Optional, Any

# Configure logger
logger = logging.getLogger(__name__)

class NutritionAgent:
    """
    Agent responsible for realistic multi-item meal planning with pairing logic.
    """

    def __init__(self, csv_path: str = "data/expanded_food_dataset_2500.csv"):
        self.csv_path = csv_path
        self.df = None
        self._load_data()
        
        # Define Pairing Logic
        # Key = The category of the Main Dish
        # Value = List of categories suitable for Side Dish
        self.pairing_rules = {
            "curry": ["rice", "flatbread", "dry_veg"], # Dal -> Rice/Roti
            "dry_veg": ["flatbread", "rice", "curry"], # Paneer Bhurji -> Roti
            "rice": ["curry", "dry_veg", "yogurt"],    # Biryani -> Raita
            "soup": ["bread", "salad"],                # Tomato Soup -> Toast
            "pasta": ["salad", "soup", "bread"],       # Pasta -> Garlic Bread
            "breakfast_item": ["beverage", "fruit"],   # Poha -> Tea/Fruit
            "oats": ["fruit", "milk", "nuts"],         # Oats -> Apple
        }

    # ---------- DATA LOADING ----------
    def _load_data(self):
        """Loads and cleans the dataset."""
        if not os.path.exists(self.csv_path):
            raise FileNotFoundError(f"Dataset not found: {self.csv_path}")

        try:
            self.df = pd.read_csv(self.csv_path)
            # Clean headers
            self.df.columns = self.df.columns.str.strip().str.lower()
            
            # Map your specific CSV headers to internal standard keys
            # Adjust these if your CSV headers are different (e.g., "Protein_g" vs "protein")
            self.df.rename(columns={
                "food_item": "name",
                "calories": "calories",
                "protein_g": "protein",
                "carbs_g": "carbs",
                "fat_g": "fats",
                "diet": "diet",
                "meal": "meal_time"
            }, inplace=True)

            # Clean text data
            for col in ["name", "diet", "meal_time"]:
                if col in self.df.columns:
                    self.df[col] = self.df[col].astype(str).str.lower().str.strip()
            
            # Create 'category' column if it doesn't exist
            if "category" not in self.df.columns:
                logger.info("Category column missing. Using AI inference to guess categories.")
                self.df["category"] = self.df["name"].apply(self._infer_category)

            logger.info(f"Nutrition dataset loaded: {len(self.df)} rows")

        except Exception as e:
            logger.error(f"Failed to load dataset: {e}")
            raise

    # ---------- CORE LOGIC ----------
    def recommend_meal_plan(self, diet_preference: str, total_calories: float) -> Dict[str, Any]:
        """
        Generates a full day's meal plan (Breakfast, Lunch, Dinner).
        """
        diet_pref = diet_preference.lower().strip()
        
        # Filter by diet (Veg/Non-Veg)
        # We use .str.contains to be flexible (e.g., 'veg' matches 'vegan' too, be careful)
        diet_df = self.df[self.df["diet"].str.contains(diet_pref, na=False)].copy()
        
        if diet_df.empty:
            return {"error": f"No foods found for diet: {diet_preference}"}

        # Calorie distribution
        splits = {
            "Breakfast": 0.25,
            "Lunch": 0.40,
            "Dinner": 0.35
        }

        meal_plan = {}

        for meal_name, ratio in splits.items():
            target = total_calories * ratio
            
            # Filter foods for this specific meal time (Breakfast/Lunch/Dinner)
            time_df = diet_df[diet_df["meal_time"] == meal_name.lower()].copy()
            
            if time_df.empty:
                # Fallback: if no specific breakfast items, use entire diet_df
                time_df = diet_df 

            combined_meal = self._build_smart_meal(time_df, target)
            meal_plan[meal_name] = combined_meal

        return meal_plan

    def _build_smart_meal(self, df: pd.DataFrame, target_calories: float) -> Dict[str, Any]:
        """
        Builds a meal using Main + Side pairing logic.
        """
        selected_items = []
        current_cals = 0

        # 1. Pick the MAIN item (High Calorie / Protein)
        # We prefer high protein items as mains usually
        main_candidates = df.sort_values("calories", ascending=False).head(int(len(df)*0.5))
        
        if main_candidates.empty:
            return {"items": [], "total_calories": 0}

        main_item = main_candidates.sample(1).iloc[0]
        selected_items.append(self._format_item(main_item, role="Main"))
        current_cals += main_item["calories"]

        # 2. Determine compatible sides
        main_cat = main_item.get("category", "generic")
        compatible_cats = self.pairing_rules.get(main_cat, [])
        
        # 3. Pick SIDE item (that matches the Main)
        remaining_cals = target_calories - current_cals
        
        if remaining_cals > 50: # Only add side if we have room
            # Filter df for compatible categories
            if compatible_cats:
                side_candidates = df[df["category"].isin(compatible_cats)]
            else:
                side_candidates = df # No specific rule? Pick anything.

            # Don't pick the exact same item again
            side_candidates = side_candidates[side_candidates["name"] != main_item["name"]]

            # Find closest calorie match
            if not side_candidates.empty:
                side_candidates = side_candidates.copy()
                side_candidates["diff"] = (side_candidates["calories"] - remaining_cals).abs()
                best_side = side_candidates.sort_values("diff").head(3).sample(1).iloc[0]
                
                selected_items.append(self._format_item(best_side, role="Side"))
                current_cals += best_side["calories"]

        return {
            "items": selected_items,
            "total_calories": int(current_cals),
            "macro_summary": self._sum_macros(selected_items)
        }

    # ---------- HELPERS ----------
    def _infer_category(self, name: str) -> str:
        """
        Heuristics to categorize food if 'Category' column is missing.
        """
        n = name.lower()
        if any(x in n for x in ["dal", "lentil", "sambar", "curry", "paneer", "chicken", "fish", "gravy"]):
            return "curry"
        elif any(x in n for x in ["rice", "biryani", "pulao", "khichdi"]):
            return "rice"
        elif any(x in n for x in ["roti", "chapati", "naan", "paratha", "bread", "toast"]):
            return "flatbread"
        elif any(x in n for x in ["soup", "broth", "rasam"]):
            return "soup"
        elif any(x in n for x in ["salad", "sprouts", "cucumber"]):
            return "salad"
        elif any(x in n for x in ["oats", "porridge", "cereal", "muesli", "upma", "poha", "idli", "dosa"]):
            return "breakfast_item"
        elif any(x in n for x in ["milk", "shake", "tea", "coffee", "juice"]):
            return "beverage"
        elif any(x in n for x in ["apple", "banana", "fruit", "papaya"]):
            return "fruit"
        else:
            return "generic"

    def _format_item(self, item: pd.Series, role: str) -> Dict[str, Any]:
        return {
            "name": item["name"].title(),
            "role": role,
            "calories": int(item["calories"]),
            "protein": float(item["protein"]),
            "carbs": float(item["carbs"]),
            "fats": float(item["fats"])
        }

    def _sum_macros(self, items: List[Dict]) -> Dict[str, float]:
        return {
            "protein": sum(i["protein"] for i in items),
            "carbs": sum(i["carbs"] for i in items),
            "fats": sum(i["fats"] for i in items)
        }