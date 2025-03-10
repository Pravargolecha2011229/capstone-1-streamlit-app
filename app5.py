import streamlit as st
import pandas as pd
import random
import datetime
import os
from PIL import Image
import io
import base64
import google.generativeai as genai
from google.api_core.exceptions import InvalidArgument
import numpy as np
import matplotlib.pyplot as plt

# App title and configuration
st.set_page_config(
    page_title="FutureEats - Smart Restaurant Management",
    page_icon="🍴",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Gemini API Configuration
def configure_genai():
    api_key = st.secrets.get("AIzaSyBHf20B9RLgXxn0mhCSEhJWilRG6QhM_jk", None)
    
    if not api_key:
        api_key = st.sidebar.text_input("Enter Gemini API Key:", type="password")
        if not api_key:
            st.sidebar.warning("Please enter a valid Gemini API key to enable AI features")
            return False
    
    try:
        genai.configure(api_key=api_key)
        return True
    except Exception as e:
        st.sidebar.error(f"Error configuring Gemini API: {str(e)}")
        return False

# Sample data creation
def create_sample_data():
    # Sample dishes data
    dishes = [
        {"name": "Quinoa Bowl", "category": "Main", "ingredients": ["quinoa", "avocado", "tomatoes", "spinach", "olive oil", "lemon juice"], "dietary": ["vegan", "gluten-free"], "price": 12.99, "feedback_score": 4.7},
        {"name": "Grilled Salmon", "category": "Main", "ingredients": ["salmon", "lemon", "dill", "olive oil", "garlic", "black pepper"], "dietary": ["keto", "paleo"], "price": 18.99, "feedback_score": 4.8},
        {"name": "Kale Caesar Salad", "category": "Starter", "ingredients": ["kale", "croutons", "parmesan", "caesar dressing", "lemon juice"], "dietary": ["vegetarian"], "price": 9.99, "feedback_score": 4.2},
        {"name": "Lentil Soup", "category": "Starter", "ingredients": ["lentils", "carrots", "celery", "onion", "vegetable broth", "cumin"], "dietary": ["vegan", "gluten-free"], "price": 7.99, "feedback_score": 4.5},
        {"name": "Berry Smoothie Bowl", "category": "Breakfast", "ingredients": ["mixed berries", "banana", "almond milk", "chia seeds", "granola"], "dietary": ["vegetarian"], "price": 10.99, "feedback_score": 4.6},
        {"name": "Avocado Toast", "category": "Breakfast", "ingredients": ["sourdough bread", "avocado", "cherry tomatoes", "microgreens", "olive oil", "sea salt"], "dietary": ["vegetarian"], "price": 8.99, "feedback_score": 4.4},
        {"name": "Zucchini Noodles", "category": "Main", "ingredients": ["zucchini", "cherry tomatoes", "basil", "garlic", "olive oil", "pine nuts"], "dietary": ["vegan", "gluten-free", "keto"], "price": 14.99, "feedback_score": 4.3},
        {"name": "Chia Pudding", "category": "Dessert", "ingredients": ["chia seeds", "coconut milk", "maple syrup", "vanilla extract", "fresh berries"], "dietary": ["vegan", "gluten-free"], "price": 6.99, "feedback_score": 4.1},
        {"name": "Sweet Potato Fries", "category": "Side", "ingredients": ["sweet potato", "olive oil", "paprika", "sea salt", "black pepper"], "dietary": ["vegan", "gluten-free"], "price": 5.99, "feedback_score": 4.9},
        {"name": "Hummus Platter", "category": "Appetizer", "ingredients": ["chickpeas", "tahini", "olive oil", "lemon juice", "garlic", "pita bread", "cucumber", "carrots"], "dietary": ["vegetarian"], "price": 11.99, "feedback_score": 4.6},
    ]
    
    # Create a weekly menu for 31 days
    start_date = datetime.date(2025, 3, 1)
    weekly_menu = []
    
    for i in range(31):
        current_date = start_date + datetime.timedelta(days=i)
        day_menu = []
        
        # Add 4-6 dishes for each day
        num_dishes = random.randint(4, 6)
        selected_dishes = random.sample(dishes, num_dishes)
        
        for dish in selected_dishes:
            # Add some randomness to feedback scores
            feedback_variation = round(random.uniform(-0.2, 0.2), 1)
            adjusted_score = min(5.0, max(1.0, dish["feedback_score"] + feedback_variation))
            
            day_menu.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "day_of_week": current_date.strftime("%A"),
                "dish_name": dish["name"],
                "category": dish["category"],
                "ingredients": dish["ingredients"],
                "dietary_tags": dish["dietary"],
                "price": dish["price"],
                "feedback_score": adjusted_score,
                "orders": random.randint(5, 50)
            })
        
        weekly_menu.extend(day_menu)
    
    # Convert to DataFrame
    menu_df = pd.DataFrame(weekly_menu)
    
    # Create sample inventory data
    ingredients_list = []
    for dish in dishes:
        ingredients_list.extend(dish["ingredients"])
    
    unique_ingredients = list(set(ingredients_list))
    
    inventory = []
    for ingredient in unique_ingredients:
        inventory.append({
            "ingredient": ingredient,
            "current_stock": random.randint(1, 10),
            "unit": random.choice(["kg", "g", "pcs", "liters", "ml"]),
            "expiry_date": (start_date + datetime.timedelta(days=random.randint(1, 14))).strftime("%Y-%m-%d"),
            "last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    
    inventory_df = pd.DataFrame(inventory)
    
    # Create sample staff data for gamification
    staff = [
        {"name": "Alex Johnson", "role": "Head Chef", "points": random.randint(1000, 5000)},
        {"name": "Sam Williams", "role": "Sous Chef", "points": random.randint(1000, 5000)},
        {"name": "Jamie Lee", "role": "Line Cook", "points": random.randint(1000, 5000)},
        {"name": "Taylor Smith", "role": "Pastry Chef", "points": random.randint(1000, 5000)},
        {"name": "Jordan Brown", "role": "Event Manager", "points": random.randint(1000, 5000)},
        {"name": "Casey Martinez", "role": "Marketing Manager", "points": random.randint(1000, 5000)},
    ]
    
    staff_df = pd.DataFrame(staff)
    
    return menu_df, inventory_df, staff_df

# Function to get AI response from Gemini
def get_gemini_response(prompt, model="gemini-1.5-pro"):
    if not configure_genai():
        return "Please configure the Gemini API key to use AI features."
    
    try:
        model = genai.GenerativeModel(model)
        response = model.generate_content(prompt)
        return response.text
    except InvalidArgument as e:
        return f"API Error: {str(e)}"
    except Exception as e:
        return f"Error generating response: {str(e)}"

# Function to generate recipe ideas
def generate_recipe_ideas(available_ingredients, seasonal_ingredients=None):
    ingredients_str = ", ".join(available_ingredients)
    seasonal_str = ", ".join(seasonal_ingredients) if seasonal_ingredients else "None specified"
    
    prompt = f"""
    As a culinary AI assistant for a health-oriented restaurant, create 3 innovative recipe ideas based on these available ingredients:
    {ingredients_str}
    
    Seasonal ingredients available: {seasonal_str}
    
    For each recipe, provide:
    1. A creative name
    2. Brief description (1-2 sentences)
    3. Key ingredients and simple preparation method
    4. Dietary tags (e.g., vegan, gluten-free, keto)
    
    Focus on health-conscious recipes that would appeal to customers of a restaurant like 'Eat Fit'.
    """
    
    response = get_gemini_response(prompt)
    return response

# Function to generate leftover ideas
def generate_leftover_ideas(leftover_ingredients):
    ingredients_str = ", ".join(leftover_ingredients)
    
    prompt = f"""
    As a sustainability-focused culinary AI, suggest 2-3 creative ways to use these leftover ingredients in tomorrow's menu:
    {ingredients_str}
    
    For each suggestion, provide:
    1. A dish name
    2. Brief description (1-2 sentences)
    3. How to incorporate the leftover ingredients
    4. What additional ingredients might be needed
    5. Which meal period it would best suit (breakfast, lunch, dinner)
    
    Focus on minimizing waste while maintaining a high-quality, health-oriented menu for a restaurant like 'Eat Fit'.
    """
    
    response = get_gemini_response(prompt)
    return response

# Function to generate promotions
def generate_promotions(promotion_type, target_audience=None, menu_items=None):
    menu_items_str = ", ".join(menu_items) if menu_items else "all menu items"
    audience_str = target_audience if target_audience else "all customers"
    
    prompt = f"""
    As a restaurant marketing AI, create 2 compelling promotional ideas for a health-oriented restaurant.
    
    Promotion type: {promotion_type}
    Target audience: {audience_str}
    Menu items to promote: {menu_items_str}
    
    For each promotion, provide:
    1. A catchy name/title
    2. Description of the offer (1-2 sentences)
    3. Suggested timeframe (e.g., weekday lunch, weekend dinner)
    4. How to present this to customers (e.g., table cards, social media)
    5. Expected benefits for the restaurant
    
    Make the promotions creative, engaging, and aligned with a health-conscious brand.
    """
    
    response = get_gemini_response(prompt)
    return response

# Function to generate event planning ideas
def generate_event_ideas(event_type, num_guests, special_requests=None):
    requests_str = special_requests if special_requests else "None specified"
    
    prompt = f"""
    As an event planning AI for a health-oriented restaurant, create a detailed plan for this event:
    
    Event type: {event_type}
    Number of guests: {num_guests}
    Special requests: {requests_str}
    
    Please provide:
    1. A creative theme suggestion
    2. Recommended seating arrangement
    3. 4-5 menu items that would work well for this event
    4. 2-3 decoration ideas
    5. Timeline suggestion (from guest arrival to conclusion)
    6. Any special touches to make the event memorable
    
    Focus on creating a health-conscious experience that aligns with a restaurant like 'Eat Fit'.
    """
    
    response = get_gemini_response(prompt)
    return response

# Function for visual menu personalization
def personalize_menu(dietary_preferences=None, image_data=None):
    if image_data:
        # In a real app, you would process the image using Gemini's multimodal capabilities
        prompt_text = "Based on the uploaded food image and"
    else:
        prompt_text = "Based on"
    
    preferences_str = ", ".join(dietary_preferences) if dietary_preferences else "no specific dietary preferences"
    
    prompt = f"""
    {prompt_text} these dietary preferences: {preferences_str}
    
    As a culinary AI for a health-oriented restaurant, suggest 4 personalized menu items that would appeal to this customer.
    
    For each menu item, provide:
    1. Dish name
    2. Brief description (1-2 sentences)
    3. Key ingredients 
    4. Why it suits the customer's preferences
    5. Suggested customizations if any
    
    Make the suggestions health-conscious, flavorful, and visually appealing.
    """
    
    response = get_gemini_response(prompt)
    return response

# Create placeholder charts and visualizations
def create_placeholder_charts():
    # Create a sample sales data chart
    dates = [f"Mar {i}" for i in range(1, 11)]
    sales = [random.randint(2000, 5000) for _ in range(10)]
    
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(dates, sales, marker='o', linestyle='-', color='#2A9D8F')
    ax.set_title('Daily Sales (Last 10 Days)')
    ax.set_xlabel('Date')
    ax.set_ylabel('Sales ($)')
    ax.grid(True, linestyle='--', alpha=0.7)
    st.pyplot(fig)
    
    # Create two column charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Top dishes by order
        dishes = ['Quinoa Bowl', 'Grilled Salmon', 'Berry Smoothie', 'Avocado Toast', 'Kale Salad']
        orders = [random.randint(50, 200) for _ in range(5)]
        
        fig, ax = plt.subplots(figsize=(8, 4))
        bars = ax.bar(dishes, orders, color='#F4A261')
        ax.set_title('Top 5 Dishes (This Week)')
        ax.set_xlabel('Dish')
        ax.set_ylabel('Orders')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        st.pyplot(fig)
    
    with col2:
        # Waste reduction data
        weeks = ['Week 1', 'Week 2', 'Week 3', 'Week 4']
        waste = [15, 12, 8, 5]  # Decreasing trend
        
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(weeks, waste, marker='s', linestyle='-', color='#E76F51', linewidth=2)
        ax.set_title('Food Waste Reduction (kg)')
        ax.set_xlabel('Period')
        ax.set_ylabel('Waste (kg)')
        ax.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        st.pyplot(fig)

# Main app
def main():
    # Create sidebar navigation
    st.sidebar.title("FutureEats")
    st.sidebar.image("https://via.placeholder.com/150x150.png?text=FutureEats", width=150)
    
    # Navigation
    page = st.sidebar.radio(
        "Navigation",
        ["Dashboard", "AI Recipe Generator", "Leftover Management", 
         "Promotion Generator", "Event Planner", "Visual Menu Personalization", 
         "Staff Leaderboards", "Settings"]
    )
    
    # Load or create sample data
    menu_df, inventory_df, staff_df = create_sample_data()
    
    # Configure API
    api_configured = configure_genai()
    
    # Pages
    if page == "Dashboard":
        st.title("🍴 FutureEats Dashboard")
        st.subheader("Smart Restaurant Management powered by AI")
        
        # Key metrics
        metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)
        with metrics_col1:
            st.metric("Today's Orders", f"{random.randint(80, 150)}", f"{random.randint(-10, 20)}%")
        with metrics_col2:
            st.metric("Revenue", f"${random.randint(2000, 5000)}", f"{random.randint(-10, 20)}%")
        with metrics_col3:
            st.metric("Waste Reduction", f"{random.randint(40, 90)}%", f"{random.randint(5, 15)}%")
        with metrics_col4:
            st.metric("Customer Satisfaction", f"{random.randint(85, 98)}%", f"{random.randint(-5, 10)}%")
        
        # Charts
        st.subheader("Performance Overview")
        create_placeholder_charts()
        
        # Today's menu
        st.subheader("Today's Menu")
        today = datetime.date.today().strftime("%Y-%m-%d")
        # Filter for a random day since we're using sample data
        sample_day = menu_df["date"].unique()[0]
        today_menu = menu_df[menu_df["date"] == sample_day]
        
        # Display in a nicer format with cards
        menu_cols = st.columns(3)
        for i, (_, dish) in enumerate(today_menu.iterrows()):
            col_idx = i % 3
            with menu_cols[col_idx]:
                st.markdown(f"""
                <div style="border:1px solid #ddd; padding:10px; border-radius:5px; margin-bottom:10px;">
                <h3>{dish['dish_name']}</h3>
                <p><strong>Category:</strong> {dish['category']}</p>
                <p><strong>Price:</strong> ${dish['price']}</p>
                <p><strong>Feedback:</strong> {'⭐' * int(round(dish['feedback_score']))}</p>
                <p><small>Dietary: {', '.join(dish['dietary_tags'])}</small></p>
                </div>
                """, unsafe_allow_html=True)
        
        # Upcoming events
        st.subheader("Upcoming Events")
        events = [
            {"name": "Corporate Wellness Lunch", "date": "Mar 15, 2025", "guests": 25},
            {"name": "Yoga & Brunch", "date": "Mar 20, 2025", "guests": 40},
            {"name": "Cooking Workshop", "date": "Mar 25, 2025", "guests": 15}
        ]
        
        for event in events:
            st.markdown(f"""
            <div style="border:1px solid #ddd; padding:10px; border-radius:5px; margin-bottom:10px;">
            <h3>{event['name']}</h3>
            <p><strong>Date:</strong> {event['date']}</p>
            <p><strong>Guests:</strong> {event['guests']}</p>
            </div>
            """, unsafe_allow_html=True)
    
    elif page == "AI Recipe Generator":
        st.title("🧪 AI Recipe Generator")
        st.write("Generate innovative recipe ideas based on available ingredients")
        
        # Form for recipe generation
        with st.form("recipe_form"):
            # Multi-select for available ingredients
            all_ingredients = list(set([item for sublist in [dish["ingredients"] for _, dish in menu_df.iterrows()] for item in sublist]))
            available_ingredients = st.multiselect(
                "Select available ingredients:",
                options=sorted(all_ingredients),
                default=sorted(all_ingredients)[:5]
            )
            
            # Seasonal ingredients
            seasonal_ingredients = st.multiselect(
                "Select seasonal ingredients (optional):",
                options=["asparagus", "strawberries", "rhubarb", "peas", "radishes", "artichokes", "spring onions"]
            )
            
            st.markdown("### Recipe Challenge")
            st.write("Submit your recipe to the weekly challenge for a chance to earn points!")
            
            challenge_theme = st.selectbox(
                "Current Challenge Theme:",
                ["Spring Renewal", "Plant-Based Power", "Breakfast Revolution", "Superfood Spotlight"]
            )
            
            submitted = st.form_submit_button("Generate Recipe Ideas")
        
        if submitted:
            if api_configured:
                with st.spinner('Generating recipe ideas...'):
                    recipe_ideas = generate_recipe_ideas(available_ingredients, seasonal_ingredients)
                    st.success("Recipe ideas generated!")
                    st.markdown(recipe_ideas)
                    
                    # Gamification element
                    st.markdown("---")
                    st.subheader("Recipe Challenge Leaderboard")
                    
                    # Sample leaderboard data
                    leaderboard = staff_df.sort_values("points", ascending=False).head()
                    
                    for i, (_, chef) in enumerate(leaderboard.iterrows()):
                        st.markdown(f"""
                        <div style="display:flex; align-items:center; margin-bottom:10px;">
                            <div style="width:30px; font-weight:bold;">{i+1}.</div>
                            <div style="flex-grow:1;">{chef['name']} ({chef['role']})</div>
                            <div style="width:100px; text-align:right;">{chef['points']} pts</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # UI for submitting to challenge
                    st.markdown("---")
                    st.subheader("Submit Your Creation")
                    recipe_name = st.text_input("Recipe Name:")
                    recipe_description = st.text_area("Recipe Description:")
                    photo_upload = st.file_uploader("Upload Recipe Photo (optional)", type=["jpg", "png", "jpeg"])
                    
                    if st.button("Submit to Challenge"):
                        st.success("Recipe submitted to the challenge! You earned 50 points!")
            else:
                st.error("Please configure the Gemini API key in Settings to use this feature.")
    
    elif page == "Leftover Management":
        st.title("♻️ Leftover Management")
        st.write("Minimize food waste by getting creative ideas for using leftover ingredients")
        
        # Form for leftover management
        with st.form("leftover_form"):
            # Get inventory items that are low in stock or near expiry
            expiring_soon = inventory_df[pd.to_datetime(inventory_df['expiry_date']) <= (datetime.datetime.now() + datetime.timedelta(days=3))]
            low_stock = inventory_df[inventory_df['current_stock'] <= 2]
            
            st.subheader("Ingredients to Use Soon")
            
            # Display expiring ingredients
            if not expiring_soon.empty:
                st.markdown("#### Expiring Soon:")
                for _, item in expiring_soon.iterrows():
                    st.markdown(f"- {item['ingredient']} ({item['current_stock']} {item['unit']}) - Expires: {item['expiry_date']}")
            
            # Display low stock ingredients
            if not low_stock.empty:
                st.markdown("#### Low Stock:")
                for _, item in low_stock.iterrows():
                    st.markdown(f"- {item['ingredient']} ({item['current_stock']} {item['unit']})")
            
            # Multi-select for leftover ingredients
            leftover_options = sorted(inventory_df['ingredient'].tolist())
            leftover_ingredients = st.multiselect(
                "Select leftover ingredients to use:",
                options=leftover_options,
                default=expiring_soon['ingredient'].tolist() if not expiring_soon.empty else leftover_options[:3]
            )
            
            generate_button = st.form_submit_button("Generate Leftover Ideas")
        
        if generate_button:
            if api_configured:
                with st.spinner('Generating ideas for leftover ingredients...'):
                    leftover_ideas = generate_leftover_ideas(leftover_ingredients)
                    st.success("Leftover ideas generated!")
                    st.markdown(leftover_ideas)
                    
                    # Gamification element
                    st.markdown("---")
                    st.subheader("Waste Reduction Leaderboard")
                    
                    # Create a sample waste reduction chart
                    staff_names = staff_df['name'].tolist()
                    waste_reduction = [random.randint(40, 95) for _ in range(len(staff_names))]
                    
                    fig, ax = plt.subplots(figsize=(10, 5))
                    bars = ax.barh(staff_names, waste_reduction, color='#2A9D8F')
                    ax.set_title('Waste Reduction by Staff Member (%)')
                    ax.set_xlabel('Waste Reduction (%)')
                    ax.set_xlim(0, 100)
                    
                    # Add waste reduction percentage at the end of each bar
                    for i, v in enumerate(waste_reduction):
                        ax.text(v + 1, i, f"{v}%", va='center')
                    
                    plt.tight_layout()
                    st.pyplot(fig)
                    
                    # Add badges
                    st.markdown("### Achievements")
                    badges = {
                        "Waste Warrior": "Reduced waste by 50%",
                        "Eco Champion": "Implemented 3+ sustainable practices",
                        "Leftover Legend": "Created 10+ dishes from leftovers"
                    }
                    
                    badge_cols = st.columns(3)
                    for i, (badge, description) in enumerate(badges.items()):
                        with badge_cols[i]:
                            st.markdown(f"""
                            <div style="border:1px solid #ddd; padding:15px; border-radius:5px; text-align:center;">
                            <h4>{badge}</h4>
                            <p>{description}</p>
                            </div>
                            """, unsafe_allow_html=True)
            else:
                st.error("Please configure the Gemini API key in Settings to use this feature.")
    
    elif page == "Promotion Generator":
        st.title("📢 Promotion Generator")
        st.write("Create compelling promotional offers using AI")
        
        # Form for promotion generation
        with st.form("promotion_form"):
            promotion_type = st.selectbox(
                "Type of promotion:",
                ["Discount", "Buy One Get One", "Happy Hour", "Loyalty Reward", "Special Event", "Limited Time Offer"]
            )
            
            target_audience = st.selectbox(
                "Target audience:",
                ["All customers", "New customers", "Loyal customers", "Health enthusiasts", "Families", "Corporate clients"]
            )
            
            # Get menu items
            menu_items = sorted(menu_df['dish_name'].unique().tolist())
            selected_items = st.multiselect(
                "Menu items to promote (optional):",
                options=menu_items,
                default=[]
            )
            
            generate_promo_button = st.form_submit_button("Generate Promotion Ideas")
        
        if generate_promo_button:
            if api_configured:
                with st.spinner('Generating promotion ideas...'):
                    promotion_ideas = generate_promotions(promotion_type, target_audience, selected_items)
                    st.success("Promotion ideas generated!")
                    st.markdown(promotion_ideas)
                    
                    # Gamification element
                    st.markdown("---")
                    st.subheader("Promotion Contest")
                    
                    st.markdown("""
                    ### Monthly Promotion Creation Contest
                    Submit your creative promotional ideas. The winning promotion will be implemented next month!
                    """)
                    
                    # Sample previous winners
                    st.markdown("#### Previous Winners:")
                    winners = [
                        {"name": "Wellness Wednesday", "creator": "Jordan Brown", "month": "February"},
                        {"name": "Sustainable Saturdays", "creator": "Casey Martinez", "month": "January"},
                    ]
                    
                    for winner in winners:
                        st.markdown(f"""
                        <div style="border:1px solid #ddd; padding:10px; border-radius:5px; margin-bottom:10px;">
                        <h4>{winner['name']}</h4>
                        <p>Created by: {winner['creator']} | Month: {winner['month']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # UI for submitting a promotion
                    st.markdown("---")
                    st.subheader("Submit Your Promotion Idea")
                    promo_name = st.text_input("Promotion Name:")
                    promo_description = st.text_area("Promotion Description:")
                    promo_duration = st.selectbox("Duration:", ["1 week", "2 weeks", "1 month", "Recurring"])
                    
                    if st.button("Submit Promotion Idea"):
                        st.success("Promotion idea submitted! You earned 75 points!")
            else:
                st.error("Please configure the Gemini API key in Settings to use this feature.")
    
    elif page == "Event Planner":
        st.title("🎉 Event Planner")
        st.write("Plan and manage private events and themed parties with AI assistance")
        
        # Form for event planning
        with st.form("event_form"):
            event_type = st.selectbox(
                "Type of event:",
                ["Birthday Party", "Corporate Gathering", "Wedding Reception", "Wellness Retreat", 
                 "Cooking Class", "Product Launch", "Anniversary", "Team Building"]
            )
            
            num_guests = st.number_input("Number of guests:", min_value=5, max_value=200, value=30)
            
            special_requests = st.text_area(
                "Special requests or theme ideas (optional):",
                placeholder="E.g., Vegan menu, Mediterranean theme, Interactive cooking stations..."
            )
            
            generate_event_button = st.form_submit_button("Generate Event Plan")
        
        if generate_event_button:
            if api_configured:
                with st.spinner('Generating event plan...'):
                    event_plan = generate_event_ideas(event_type, num_guests, special_requests)
                    st.success("Event plan generated!")
                    st.markdown(event_plan)
                    
                    # Gamification element
                    st.markdown("---")
                    st.subheader("Event Planning Leaderboard")
                    
                    # Sample events data
                    events_data = [
                        {"name": "Corporate Wellness Retreat", "planner": "Jordan Brown", "guests": 45, "rating": 4.9},
                        {"name": "Cooking Workshop Series", "planner": "Alex Johnson", "guests": 25, "rating": 4.8},
                        {"name": "Product Launch Brunch", "planner": "Casey Martinez", "guests": 60, "rating": 4.7},
                        {"name": "Team Building Dinner", "planner": "Taylor Smith", "guests": 30, "rating": 4.6},
                    ]
                    
                    # Convert to DataFrame for display
                    events_df = pd.DataFrame(events_data)
                    events_df["success_score"] = events_df["rating"] * (events_df["guests"] / 10)
                    events_df = events_df.sort_values("success_score", ascending=False)
                    
                    st.markdown("#### Top Events (Last 3 Months)")
                    for i, (_, event) in enumerate(events_df.iterrows()):
                        st.markdown(f"""
                        <div style="border:1px solid #ddd; padding:10px; border-radius:5px; margin-bottom:10px;">
                        <h3>{event['name']}</h3>
                        <p><strong>Planner:</strong> {event['planner']}</p>
                        <p><strong>Guests:</strong> {event['guests']}</p>
                        <p><strong>Rating:</strong> {event['rating']} / 5.0</p>
                        </div>
                        """, unsafe_allow_html=True)