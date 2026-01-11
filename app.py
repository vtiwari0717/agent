"""
MacroMind AI - Premium Diet Planner

This is the user interface layer. It collects user inputs,
calls the RecommendationEngine, and displays the 7-day plan
in a modern, interactive dashboard format.
"""

import streamlit as st
import logging
import plotly.graph_objects as go
from services.recommendation_engine import RecommendationEngine

# -------------------------------------------------
# 1. PAGE CONFIGURATION (Must be first)
# -------------------------------------------------
st.set_page_config(
    page_title="MacroMind AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -------------------------------------------------
# 2. CUSTOM CSS - PREMIUM DARK MODE THEME
# -------------------------------------------------
def inject_custom_css():
    st.markdown("""
    <style>
    /* Import Modern Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main Background */
    .stApp {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1a2e 50%, #16213e 100%);
    }
    
    /* Remove Default Padding */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }
    
    /* Hero Section */
    .hero-section {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.15) 100%);
        border-radius: 20px;
        padding: 3rem 2rem;
        margin-bottom: 2rem;
        border: 1px solid rgba(102, 126, 234, 0.3);
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    
    .hero-section::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(102, 126, 234, 0.1) 0%, transparent 70%);
        animation: pulse 4s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); opacity: 0.5; }
        50% { transform: scale(1.1); opacity: 0.8; }
    }
    
    .hero-logo {
        font-size: 4rem;
        margin-bottom: 0.5rem;
    }
    
    .hero-title {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        position: relative;
        z-index: 1;
    }
    
    .hero-tagline {
        font-size: 1.3rem;
        color: #b0b0b0;
        font-weight: 400;
        letter-spacing: 0.5px;
        position: relative;
        z-index: 1;
    }
    
    /* Headers */
    h1 {
        color: #ffffff;
        font-weight: 700;
        font-size: 2.5rem !important;
        margin-bottom: 1rem;
    }
    
    h2 {
        color: #e0e0e0;
        font-weight: 600;
        font-size: 1.8rem !important;
    }
    
    h3 {
        color: #b0b0b0;
        font-weight: 500;
        font-size: 1.3rem !important;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
        border-right: 1px solid rgba(102, 126, 234, 0.2);
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: #e0e0e0;
    }
    
    /* Sidebar Headers */
    [data-testid="stSidebar"] h2 {
        color: #ffffff;
        font-size: 1.3rem !important;
        margin-top: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid rgba(102, 126, 234, 0.3);
    }
    
    /* Input Fields */
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(102, 126, 234, 0.3) !important;
        border-radius: 8px !important;
        color: #ffffff !important;
        font-weight: 500;
    }
    
    .stNumberInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus {
        border-color: rgba(102, 126, 234, 0.8) !important;
        box-shadow: 0 0 0 1px rgba(102, 126, 234, 0.4) !important;
    }
    
    /* Primary Button */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1.1rem;
        letter-spacing: 0.5px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    
    /* Dashboard Metric Cards */
    .dashboard-card {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        border: 1px solid rgba(102, 126, 234, 0.3);
        padding: 1.5rem;
        text-align: center;
        transition: all 0.3s ease;
        height: 100%;
    }
    
    .dashboard-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4);
        border-color: rgba(102, 126, 234, 0.5);
    }
    
    .dashboard-value {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0.5rem 0;
    }
    
    .dashboard-label {
        font-size: 0.95rem;
        color: #b0b0b0;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .dashboard-sublabel {
        font-size: 0.85rem;
        color: #888;
        margin-top: 0.3rem;
    }
    
    /* Metric Cards */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: #667eea;
    }
    
    [data-testid="stMetricLabel"] {
        color: #b0b0b0;
        font-weight: 500;
        font-size: 0.9rem;
    }
    
    /* Glassmorphism Container */
    .glass-container {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    
    /* Meal Card Styling - UPGRADED */
    .meal-card {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.12) 0%, rgba(118, 75, 162, 0.12) 100%);
        backdrop-filter: blur(10px);
        border-radius: 14px;
        border: 1px solid rgba(102, 126, 234, 0.25);
        padding: 1.3rem;
        margin: 0.5rem 0;
        transition: all 0.3s ease;
        min-height: 180px;
        display: flex;
        flex-direction: column;
    }
    
    .meal-card:hover {
        transform: translateY(-6px);
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.35);
        border-color: rgba(102, 126, 234, 0.45);
    }
    
    .meal-title {
        font-size: 1.3rem;
        font-weight: 700;
        color: #667eea;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .meal-combined {
        color: #e8e8e8;
        font-size: 1.05rem;
        font-weight: 500;
        margin: 0.8rem 0;
        padding: 0.8rem;
        background: rgba(255, 255, 255, 0.03);
        border-radius: 8px;
        border-left: 3px solid #667eea;
        flex-grow: 1;
    }
    
    .meal-footer {
        margin-top: auto;
        padding-top: 1rem;
        border-top: 1px solid rgba(102, 126, 234, 0.25);
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 0.5rem;
    }
    
    .macro-stat {
        text-align: center;
    }
    
    .macro-label {
        font-size: 0.75rem;
        color: #999;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .macro-value {
        font-size: 1.1rem;
        font-weight: 700;
        color: #667eea;
        margin-top: 0.2rem;
    }
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background-color: transparent;
        padding: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(102, 126, 234, 0.1);
        border-radius: 10px;
        color: #b0b0b0;
        font-weight: 600;
        font-size: 1rem;
        padding: 0.7rem 1.5rem;
        border: 1px solid rgba(102, 126, 234, 0.2);
        transition: all 0.2s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(102, 126, 234, 0.15);
        border-color: rgba(102, 126, 234, 0.3);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.3) 0%, rgba(118, 75, 162, 0.3) 100%);
        color: #ffffff;
        border-color: rgba(102, 126, 234, 0.5);
    }
    
    /* Progress Bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    /* Info/Success Boxes */
    .stAlert {
        background: rgba(102, 126, 234, 0.1);
        border: 1px solid rgba(102, 126, 234, 0.3);
        border-radius: 12px;
        color: #e0e0e0;
    }
    
    /* Success Box */
    [data-testid="stSuccess"] {
        background: linear-gradient(135deg, rgba(102, 234, 180, 0.1) 0%, rgba(102, 126, 234, 0.1) 100%);
        border: 1px solid rgba(102, 234, 180, 0.3);
    }
    
    /* Divider */
    hr {
        border-color: rgba(102, 126, 234, 0.2);
        margin: 2rem 0;
    }
    
    /* Slider */
    .stSlider > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Chart Container */
    .chart-container {
        background: rgba(255, 255, 255, 0.02);
        border-radius: 16px;
        border: 1px solid rgba(102, 126, 234, 0.2);
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    /* Feature Card */
    .feature-card {
        background: rgba(255, 255, 255, 0.03);
        border-left: 3px solid #667eea;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 8px;
    }
    
    .feature-card h4 {
        color: #667eea;
        margin: 0;
        font-size: 1.1rem;
    }
    
    .feature-card p {
        color: #b0b0b0;
        margin: 0.5rem 0 0 0;
    }
    </style>
    """, unsafe_allow_html=True)

# -------------------------------------------------
# 3. INITIALIZATION & CACHING
# -------------------------------------------------
@st.cache_resource
def load_engine():
    """
    Load the engine once and cache it. 
    This prevents reloading the 10,000-row dataset on every click.
    """
    try:
        return RecommendationEngine()
    except Exception as e:
        st.error(f"Failed to load application engine: {e}")
        return None

engine = load_engine()

# -------------------------------------------------
# 4. UI HELPER FUNCTIONS
# -------------------------------------------------
def render_hero_section():
    """Renders the hero section with branding."""
    st.markdown("""
    <div class="hero-section">
        <div class="hero-logo">🧠</div>
        <div class="hero-title">MacroMind AI</div>
    </div>
    """, unsafe_allow_html=True)

def render_dashboard_metrics(targets, bio):
    """Renders key metrics in a dashboard-style layout."""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="dashboard-card">
            <div class="dashboard-label">Daily Target</div>
            <div class="dashboard-value">{targets['calories']}</div>
            <div class="dashboard-sublabel">kcal/day</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="dashboard-card">
            <div class="dashboard-label">BMI Score</div>
            <div class="dashboard-value">{bio['bmi']}</div>
            <div class="dashboard-sublabel">{bio['bmi_category']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="dashboard-card">
            <div class="dashboard-label">Protein Goal</div>
            <div class="dashboard-value">{targets['protein']}</div>
            <div class="dashboard-sublabel">grams/day</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="dashboard-card">
            <div class="dashboard-label">Hydration</div>
            <div class="dashboard-value">3.5</div>
            <div class="dashboard-sublabel">liters/day</div>
        </div>
        """, unsafe_allow_html=True)

def render_meal_card_upgraded(meal_type, meal_data, emoji):
    """Renders meal cards with combined food items format."""
    
    # Combine food items with "+"
    if "items" in meal_data and meal_data["items"]:
        food_names = [item['name'] for item in meal_data["items"]]
        combined_text = " + ".join(food_names)
        
        # Calculate totals
        total_protein = sum(item['protein'] for item in meal_data["items"])
        total_carbs = sum(item['carbs'] for item in meal_data["items"])
        total_fats = sum(item['fats'] for item in meal_data["items"])
        total_cals = meal_data.get('total_calories', 0)
    else:
        combined_text = "No specific recommendation"
        total_protein = total_carbs = total_fats = total_cals = 0
    
    st.markdown(f"""
    <div class="meal-card">
        <div class="meal-title">{emoji} {meal_type}</div>
        <div class="meal-combined">{combined_text}</div>
        <div class="meal-footer">
            <div class="macro-stat">
                <div class="macro-label">Calories</div>
                <div class="macro-value">{total_cals}</div>
            </div>
            <div class="macro-stat">
                <div class="macro-label">Protein</div>
                <div class="macro-value">{int(total_protein)}g</div>
            </div>
            <div class="macro-stat">
                <div class="macro-label">Carbs</div>
                <div class="macro-value">{int(total_carbs)}g</div>
            </div>
            <div class="macro-stat">
                <div class="macro-label">Fats</div>
                <div class="macro-value">{int(total_fats)}g</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def create_macro_donut_chart(macros):
    """Creates a Plotly donut chart for macronutrient distribution."""
    labels = ['Protein', 'Carbs', 'Fats']
    values = [macros['protein'], macros['carbs'], macros['fats']]
    colors = ['#667eea', '#764ba2', '#f093fb']
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.6,
        marker=dict(colors=colors, line=dict(color='#1a1a2e', width=2)),
        textinfo='label+percent',
        textfont=dict(size=14, color='white'),
        hovertemplate='<b>%{label}</b><br>%{value}g<br>%{percent}<extra></extra>'
    )])
    
    fig.update_layout(
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=40, b=40, l=20, r=20),
        height=350,
        font=dict(family='Inter', color='white'),
        annotations=[dict(
            text=f'<b>{int(sum(values))}g</b><br>Total',
            x=0.5, y=0.5,
            font=dict(size=20, color='white'),
            showarrow=False
        )]
    )
    
    return fig

def create_progress_chart():
    """Creates a mock projected weight progress line chart."""
    days = ['Day 1', 'Day 2', 'Day 3', 'Day 4', 'Day 5', 'Day 6', 'Day 7']
    # Mock weight trend (slightly decreasing for weight loss goal)
    weights = [70, 69.8, 69.6, 69.5, 69.3, 69.2, 69.0]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=days,
        y=weights,
        mode='lines+markers',
        line=dict(color='#667eea', width=3),
        marker=dict(size=10, color='#764ba2', line=dict(color='white', width=2)),
        fill='tozeroy',
        fillcolor='rgba(102, 126, 234, 0.1)',
        hovertemplate='<b>%{x}</b><br>Weight: %{y} kg<extra></extra>'
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=40, b=40, l=40, r=40),
        height=300,
        font=dict(family='Inter', color='white'),
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(102, 126, 234, 0.1)',
            zeroline=False
        ),
        yaxis=dict(
            title='Weight (kg)',
            showgrid=True,
            gridcolor='rgba(102, 126, 234, 0.1)',
            zeroline=False
        ),
        hovermode='x unified'
    )
    
    return fig

# -------------------------------------------------
# 5. MAIN APPLICATION LOGIC
# -------------------------------------------------
def main():
    # Inject Custom CSS
    inject_custom_css()
    
    # --- HERO SECTION ---
    render_hero_section()

    # --- SIDEBAR (INPUTS) ---
    with st.sidebar:
        st.markdown("<h2>👤 Your Profile</h2>", unsafe_allow_html=True)
        
        # Biometrics
        age = st.number_input("Age", 18, 90, 25)
        gender = st.selectbox("Gender", ["Male", "Female"])
        height = st.number_input("Height (cm)", 120, 220, 170)
        weight = st.number_input("Weight (kg)", 40, 180, 70)
        
        st.divider()
        st.markdown("<h2>🎯 Goals & Lifestyle</h2>", unsafe_allow_html=True)
        
        activity_level = st.select_slider(
            "Activity Level",
            options=["Sedentary", "Lightly Active", "Moderately Active", "Very Active", "Extra Active"],
            value="Moderately Active"
        )
        
        goal = st.selectbox(
            "Health Goal",
            ["Maintenance", "Weight Loss", "Muscle Gain"],
            index=0
        )
        
        diet_pref = st.selectbox(
            "Diet Preference",
            ["Veg", "Non-Veg", "Vegan"],
            index=0
        )
        
        st.divider()
        generate_btn = st.button("✨ Generate My Plan", type="primary", use_container_width=True)

    # --- MAIN CONTENT ---
    if generate_btn:
        if not engine:
            st.error("Engine not loaded. Please check logs.")
            return

        with st.spinner("🔄 AI Agents are collaborating... Analyzing Metabolism..."):
            # Prepare Input
            user_profile = {
                "age": age,
                "gender": gender,
                "height": height,
                "weight": weight,
                "activity_level": activity_level,
                "goal": goal,
                "diet_preference": diet_pref,
                "name": "User"
            }
            
            # CALL ENGINE
            result = engine.generate_plan(user_profile)
        
        if "error" in result:
            st.error(result["error"])
        else:
            # --- DISPLAY RESULTS ---
            
            # 1. AI Insight Box
            st.markdown(f"""
            <div class="glass-container" style="background: linear-gradient(135deg, rgba(102, 234, 180, 0.1) 0%, rgba(102, 126, 234, 0.1) 100%); border-color: rgba(102, 234, 180, 0.3);">
                <div style="font-size: 1.1rem; color: #e0e0e0;">
                    <strong style="color: #66eab4;">💡 AI Coach Insight:</strong><br/>
                    {result['ai_insight']}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<br/>", unsafe_allow_html=True)
            
            # 2. Dashboard Metrics
            targets = result["nutritional_targets"]
            bio = result["biometrics"]
            render_dashboard_metrics(targets, bio)
            
            st.markdown("<br/><br/>", unsafe_allow_html=True)
            
            # 3. Main Content Tabs
            tab_plan, tab_analytics = st.tabs(["📅 Weekly Meal Plan", "📊 Analytics & Insights"])
            
            with tab_plan:
                weekly_plan = result["weekly_plan"]
                
                # Create sub-tabs for each day
                day_tabs = st.tabs([f"Day {i+1}" for i in range(7)])
                
                for idx, (day_name, day_data) in enumerate(weekly_plan.items()):
                    with day_tabs[idx]:
                        st.markdown(f"<h3>Total: {day_data['calories']} kcal</h3>", unsafe_allow_html=True)
                        st.markdown("<br/>", unsafe_allow_html=True)
                        
                        # Layout: 3 Columns for meals
                        c1, c2, c3 = st.columns(3)
                        
                        with c1:
                            render_meal_card_upgraded("Breakfast", day_data["meals"]["Breakfast"], "🍳")
                        with c2:
                            render_meal_card_upgraded("Lunch", day_data["meals"]["Lunch"], "🍛")
                        with c3:
                            render_meal_card_upgraded("Dinner", day_data["meals"]["Dinner"], "🍲")
            
            with tab_analytics:
                st.markdown("<h2>Nutrition Analytics</h2>", unsafe_allow_html=True)
                st.markdown("<br/>", unsafe_allow_html=True)
                
                # Two columns for charts
                col_left, col_right = st.columns(2)
                
                with col_left:
                    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                    st.markdown("<h3>Macronutrient Distribution</h3>", unsafe_allow_html=True)
                    day1_macros = result["weekly_plan"]["Day 1"]["macros"]
                    fig_donut = create_macro_donut_chart(day1_macros)
                    st.plotly_chart(fig_donut, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col_right:
                    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                    st.markdown("<h3>Projected Progress</h3>", unsafe_allow_html=True)
                    fig_progress = create_progress_chart()
                    st.plotly_chart(fig_progress, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                st.markdown("<br/>", unsafe_allow_html=True)
                
                # Detailed Macro Breakdown
                st.markdown('<div class="glass-container">', unsafe_allow_html=True)
                st.markdown("<h3>Daily Macro Targets</h3>", unsafe_allow_html=True)
                
                c1, c2, c3 = st.columns(3)
                
                with c1:
                    st.metric("Protein Target", f"{targets['protein']}g")
                    p_val = min(day1_macros['protein'] / (targets['protein'] + 0.1), 1.0)
                    st.progress(p_val, text=f"Current: {day1_macros['protein']}g")
                    
                with c2:
                    st.metric("Carbs Target", f"{targets['carbs']}g")
                    c_val = min(day1_macros['carbs'] / (targets['carbs'] + 0.1), 1.0)
                    st.progress(c_val, text=f"Current: {day1_macros['carbs']}g")
                    
                with c3:
                    st.metric("Fats Target", f"{targets['fats']}g")
                    f_val = min(day1_macros['fats'] / (targets['fats'] + 0.1), 1.0)
                    st.progress(f_val, text=f"Current: {day1_macros['fats']}g")
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                st.info("💡 This plan is optimized to help you reach your goals while maintaining energy and health.")

    else:
        # Landing Page Content
        st.markdown('<div class="glass-container">', unsafe_allow_html=True)
        st.info("👈 Enter your details in the sidebar and click 'Generate My Plan' to start!")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("<br/>", unsafe_allow_html=True)
        
        # Feature Cards
        st.markdown("<h2>How It Works</h2>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="feature-card">
                <h4>🧮 Health Agent</h4>
                <p>Calculates your exact metabolic needs using advanced algorithms and scientific formulas.</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="feature-card">
                <h4>🍽️ Nutrition Agent</h4>
                <p>Scans 10,000+ foods to find the best combinations tailored to your preferences.</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="feature-card">
                <h4>🤖 Cognitive Agent</h4>
                <p>Reviews the plan to ensure it's balanced and explains the reasoning behind each choice.</p>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()