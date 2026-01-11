"""
Agents Package Initialization.

This package serves as the core intelligence layer for the AI Personalized Diet Planner.
It exposes the following agents responsible for logic flow:

- HealthAgent: Analyzes user biometrics (BMI, BMR, TDEE) and health adjustments.
- NutritionAgent: Handles caloric logic, macronutrient splits, and meal selection.
- LLMAgent: Manages interaction with the AI model for personalized text generation.
"""

import logging

# Configure a NullHandler to prevent logging warnings if the main app 
# does not configure logging.
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

# Attempt to import core agents with error handling to aid debugging
try:
    from .health_agent import HealthAgent
    from .nutrition_agent import NutritionAgent
    from .llm_agent import LLMAgent
except ImportError as e:
    logger.error(f"Failed to import core agents. Check dependencies. Error: {e}")
    raise

# Define the public API of this package
__all__ = [
    "HealthAgent",
    "NutritionAgent",
    "LLMAgent",
]

# Package version
__version__ = "1.0.0"