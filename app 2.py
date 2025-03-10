import streamlit as st
import pandas as pd
import random
from datetime import datetime, timedelta
import os
import google.generativeai as genai

# Page configuration
st.set_page_config(
    page_title="FutureEats - Smart Restaurant Management",
    page_icon="🍽️",
    layout="wide"
)

# Secure API key handling using environment variables
# IMPORTANT: Don't hardcode API keys in your app!
def initialize_gemini():
    api_key = os.environ.get('AIzaSyDKN-v5n8ymxbJU09QWWlweHQrFQIv-eJ4')
    if not api_key:
        st.sidebar.warning("⚠️ Gemini API key not found. Some AI features may be limited.")
        return None
    
    try:
        genai.configure(api_key=api_key)
        # Configure the model
        generation_config = {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 40,
        }
        
        # Initialize Gemini Pro model
        model = genai.GenerativeModel(
            model_name="gemini-1.5-pro",
            generation_config=generation_config
        )
        return model
    except Exception as e:
        st.sidebar.error(f"Error initializing Gemini: {str(e)}")
        return None

# Initialize Gemini model
gemini_model = initialize_gemini()

# Initialize session state variables if they don't exist
if 'recipe_database' not in st.session_state:
    # Create sample menu items
    menu_items = [
        {"day": "Monday", "dish": "Quinoa Salad Bowl", "ingredients": ["quinoa", "cucumber", "tomatoes", "feta cheese"], "feedback": 4.7},
        {"day": "Monday", "dish": "Grilled Chicken", "ingredients": ["chicken breast", "lemon", "herbs", "olive oil"], "feedback": 4.8},
        {"day": "Tuesday", "dish": "Mango Smoothie Bowl", "ingredients": ["mango", "banana", "almond milk", "chia seeds"], "feedback": 4.6},
        {"day": "Tuesday", "dish": "Mediterranean Wrap", "ingredients": ["wrap", "hummus", "vegetables", "feta"], "feedback": 4.5},
        {"day": "Wednesday", "dish": "Avocado Toast", "ingredients": ["bread", "avocado", "tomatoes", "microgreens"], "feedback": 4.7},
        {"day": "Wednesday", "dish": "Grilled Salmon", "ingredients": ["salmon", "lemon", "dill", "olive oil"], "feedback": 4.9},
    ]
    st.session_state.recipe_database = pd.DataFrame(menu_items)

if 'inventory' not in st.session_state:
    # Initialize basic inventory
    st.session_state.inventory = {
        "vegetables": ["spinach", "kale", "carrots", "bell peppers", "cucumber", "tomatoes"],
        "proteins": ["chicken breast", "salmon", "tofu", "eggs", "chickpeas"],
        "grains": ["quinoa", "brown rice", "bread", "oats"],
        "fruits": ["apples", "bananas", "berries", "mango", "avocado", "lemon"]
    }
    st.session_state.leftovers = ["spinach", "quinoa", "tomatoes", "feta cheese"]

if 'events' not in st.session_state:
    # Sample events
    st.session_state.events = [
        {
            "name": "Mediterranean Cuisine Night",
            "date": (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d"),
            "guests": 35,
            "theme": "Mediterranean",
            "menu": ["Greek Salad", "Hummus Platter", "Grilled Sea Bass", "Baklava"]
        },
        {
            "name": "Health & Wellness Brunch",
            "date": (datetime.now() + timedelta(days=12)).strftime("%Y-%m-%d"),
            "guests": 25,
            "theme": "Wellness",
            "menu": ["Acai Bowls", "Avocado Toast", "Egg White Frittata", "Smoothies"]
        }
    ]

if 'customer_preferences' not in st.session_state:
    # Sample customer preferences
    st.session_state.customer_preferences = [
        {"preference": "Vegetarian", "count": 45},
        {"preference": "Gluten-Free", "count": 32},
        {"preference": "Dairy-Free", "count": 28},
        {"preference": "Vegan", "count": 20},
        {"preference": "Keto", "count": 18}
    ]

# AI-enhanced helper functions using Gemini (with fallback to original functions)
def generate_recipe_suggestion_with_ai(ingredients):
    """Generate a recipe based on selected ingredients using Gemini if available"""
    if gemini_model:
        try:
            # Create a prompt for Gemini
            prompt = f"""
            Create a creative recipe using some or all of these ingredients: {', '.join(ingredients)}.
            Provide the following details in JSON format:
            - name: The recipe name
            - ingredients: List of ingredients used (subset of the provided ingredients)  
            - instructions: Simple step-by-step instructions (4-5 steps)
            - nutrition: Estimated calories, protein, and carbs
            - preparation_time: Estimated prep time in minutes
            
            Return ONLY the JSON with no additional text.
            """
            
            response = gemini_model.generate_content(prompt)
            result = response.text
            
            # Parse the response (assuming it's valid JSON)
            import json
            try:
                recipe = json.loads(result)
                # Ensure all required fields are present
                required_fields = ["name", "ingredients", "instructions", "nutrition", "preparation_time"]
                for field in required_fields:
                    if field not in recipe:
                        raise ValueError(f"Missing field: {field}")
                
                return recipe
            except (json.JSONDecodeError, ValueError) as e:
                st.warning(f"Could not parse AI response. Using backup recipe generator.")
                # Fall back to the original function
                return generate_recipe_suggestion_fallback(ingredients)
                
        except Exception as e:
            st.warning(f"AI recipe generation failed. Using backup recipe generator.")
            return generate_recipe_suggestion_fallback(ingredients)
    else:
        # If Gemini is not available, use the original function
        return generate_recipe_suggestion_fallback(ingredients)

def generate_recipe_suggestion_fallback(ingredients):
    """Generate a recipe based on selected ingredients - original function"""
    recipe_types = ["Bowl", "Salad", "Plate", "Wrap"]
    cooking_methods = ["Roasted", "Grilled", "Fresh", "Steamed"]
    
    # Select some ingredients if we have enough
    if len(ingredients) > 2:
        selected_ingredients = random.sample(ingredients, min(3, len(ingredients)))
    else:
        selected_ingredients = ingredients
    
    # Generate recipe name
    method = random.choice(cooking_methods)
    dish_type = random.choice(recipe_types)
    main_ingredient = random.choice(selected_ingredients)
    
    # Create a name based on ingredients
    other_ingredients = [i for i in selected_ingredients if i != main_ingredient]
    if other_ingredients:
        recipe_name = f"{method} {main_ingredient.title()} {dish_type} with {', '.join([i.title() for i in other_ingredients])}"
    else:
        recipe_name = f"{method} {main_ingredient.title()} {dish_type}"
    
    # Simple instructions
    instructions = [
        f"Prepare the {main_ingredient}.",
        f"Add the {', '.join(other_ingredients) if other_ingredients else 'seasonings'}.",
        "Cook for 5-7 minutes until done.",
        "Serve and enjoy!"
    ]
    
    # Nutritional info
    nutrition = {
        "calories": random.randint(250, 450),
        "protein": random.randint(15, 30),
        "carbs": random.randint(20, 45)
    }
    
    return {
        "name": recipe_name,
        "ingredients": selected_ingredients,
        "instructions": instructions,
        "nutrition": nutrition,
        "preparation_time": f"{random.randint(15, 30)} minutes"
    }

def generate_event_suggestion_with_ai(guest_count, theme):
    """Generate event planning suggestions using Gemini if available"""
    if gemini_model:
        try:
            # Create a prompt for Gemini
            prompt = f"""
            Create a detailed event planning suggestion for a {theme} themed event with {guest_count} guests.
            Provide the following details in JSON format:
            - theme_details: A brief description of the event
            - menu: A list of 4-6 suggested menu items appropriate for the theme
            - estimated_cost: Approximate cost per person (in USD)
            - preparation_time: Recommended planning time
            
            Return ONLY the JSON with no additional text.
            """
            
            response = gemini_model.generate_content(prompt)
            result = response.text
            
            # Parse the response
            import json
            try:
                event_suggestion = json.loads(result)
                # Ensure all required fields are present
                required_fields = ["theme_details", "menu", "estimated_cost", "preparation_time"]
                for field in required_fields:
                    if field not in event_suggestion:
                        raise ValueError(f"Missing field: {field}")
                
                return event_suggestion
            except (json.JSONDecodeError, ValueError) as e:
                st.warning(f"Could not parse AI response. Using backup event generator.")
                # Fall back to the original function
                return generate_event_suggestion_fallback(guest_count, theme)
                
        except Exception as e:
            st.warning(f"AI event generation failed. Using backup event generator.")
            return generate_event_suggestion_fallback(guest_count, theme)
    else:
        # If Gemini is not available, use the original function
        return generate_event_suggestion_fallback(guest_count, theme)

def generate_event_suggestion_fallback(guest_count, theme):
    """Generate event planning suggestions - original function"""
    menu_suggestions = []
    if "Mediterranean" in theme:
        menu_suggestions = ["Mezze Platter", "Grilled Sea Bass", "Lamb Souvlaki", "Baklava"]
    elif "Wellness" in theme:
        menu_suggestions = ["Acai Bowls", "Avocado Toast", "Grain Bowls", "Infused Water"]
    else:
        menu_suggestions = ["Chef's Selection Appetizers", "Seasonal Salad", "Choice of Entrees"]
    
    return {
        "theme_details": f"A {theme} themed event for {guest_count} guests",
        "menu": menu_suggestions,
        "estimated_cost": f"${random.randint(35, 75)} per person",
        "preparation_time": f"{random.randint(2, 4)} weeks planning recommended"
    }

# Main app layout with sidebar navigation
st.sidebar.title("🍽️ FutureEats")
st.sidebar.header("Restaurant Management")

# Add API status indicator in sidebar
if gemini_model:
    st.sidebar.success("✅ Gemini AI connected")
else:
    st.sidebar.info("ℹ️ Running without Gemini AI")
    st.sidebar.write("To enable AI features, set the GEMINI_API_KEY environment variable.")
    st.sidebar.code("export GEMINI_API_KEY='your_api_key_here'")

app_mode = st.sidebar.selectbox(
    "Select Feature", 
    ["Dashboard", "Recipe Suggestions", "Leftover Management", "Event Manager", "Menu Personalization"]
)

# Dashboard view
if app_mode == "Dashboard":
    st.title("🍽️ FutureEats Dashboard")
    st.subheader("Restaurant Management System")
    
    # Key metrics in columns
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Menu Items", value=len(st.session_state.recipe_database))
        st.metric(label="Upcoming Events", value=len(st.session_state.events))
    
    with col2:
        st.metric(label="Top Rated Dish", value="Grilled Salmon", delta="4.9/5")
        st.metric(label="Top Preference", value="Vegetarian", delta="45 customers")
    
    with col3:
        st.metric(label="Inventory Categories", value=len(st.session_state.inventory))
        total_inventory = sum(len(items) for items in st.session_state.inventory.values())
        st.metric(label="Total Inventory Items", value=total_inventory)
    
    # Weekly menu schedule
    st.subheader("Weekly Menu")
    st.dataframe(st.session_state.recipe_database[['day', 'dish', 'feedback']])
    
    # Customer preferences chart
    st.subheader("Customer Dietary Preferences")
    preferences_df = pd.DataFrame(st.session_state.customer_preferences)
    st.bar_chart(preferences_df.set_index('preference')['count'])
    
    # Upcoming events
    st.subheader("Upcoming Events")
    for event in st.session_state.events:
        st.write(f"**{event['name']}** - {event['date']} - {event['guests']} guests")
        st.write(f"Theme: {event['theme']}")
        st.write(f"Menu: {', '.join(event['menu'])}")
        st.write("---")

# Recipe Suggestions view
elif app_mode == "Recipe Suggestions":
    st.title("Recipe Suggestions")
    st.write("Select ingredients to get recipe ideas")
    
    # Ingredient selection
    categories = list(st.session_state.inventory.keys())
    selected_category = st.selectbox("Ingredient Category", categories)
    
    available_ingredients = st.session_state.inventory[selected_category]
    selected_ingredients = st.multiselect("Select Ingredients", available_ingredients)
    
    if st.button("Generate Recipe"):
        if selected_ingredients:
            with st.spinner("Creating your recipe..." + (" with AI assistance" if gemini_model else "")):
                # Use the AI-enhanced function if available, otherwise fallback
                recipe = generate_recipe_suggestion_with_ai(selected_ingredients)
            
            st.subheader(recipe["name"])
            
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Ingredients:**")
                for ingredient in recipe["ingredients"]:
                    st.write(f"- {ingredient.title()}")
                
                st.write(f"**Preparation Time:** {recipe['preparation_time']}")
            
            with col2:
                st.write("**Nutritional Information:**")
                if isinstance(recipe['nutrition'], dict):
                    st.write(f"Calories: {recipe['nutrition'].get('calories', 'N/A')} kcal")
                    st.write(f"Protein: {recipe['nutrition'].get('protein', 'N/A')}g")
                    st.write(f"Carbs: {recipe['nutrition'].get('carbs', 'N/A')}g")
                else:
                    st.write(recipe['nutrition'])
            
            st.write("**Instructions:**")
            if isinstance(recipe["instructions"], list):
                for i, step in enumerate(recipe["instructions"]):
                    st.write(f"{i+1}. {step}")
            else:
                st.write(recipe["instructions"])
        else:
            st.warning("Please select at least one ingredient")

# Leftover Management view
elif app_mode == "Leftover Management":
    st.title("Leftover Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Current Leftovers")
        # Display and edit current leftovers
        all_ingredients = [item for sublist in st.session_state.inventory.values() for item in sublist]
        leftover_items = st.multiselect(
            "Current Leftovers", 
            options=all_ingredients, 
            default=st.session_state.leftovers
        )
        
        if st.button("Update Leftovers"):
            st.session_state.leftovers = leftover_items
            st.success("Leftover list updated!")
    
    with col2:
        st.subheader("Leftover Recipe Ideas")
        if st.button("Get Recipe Ideas"):
            if st.session_state.leftovers:
                with st.spinner("Finding recipes for your leftovers..." + (" with AI assistance" if gemini_model else "")):
                    recipe = generate_recipe_suggestion_with_ai(st.session_state.leftovers)
                    
                    st.write(f"### {recipe['name']}")
                    st.write("A perfect way to use your leftover ingredients!")
                    
                    st.write("**Ingredients needed:**")
                    for ingredient in recipe['ingredients']:
                        st.write(f"- {ingredient.title()}")
                    
                    st.write("**Quick Instructions:**")
                    if isinstance(recipe["instructions"], list):
                        for i, step in enumerate(recipe["instructions"]):
                            st.write(f"{i+1}. {step}")
                    else:
                        st.write(recipe["instructions"])
                    
                    st.write("**Sustainability Impact:** Reduces food waste by using leftovers effectively!")
            else:
                st.info("No leftovers available. Please add some leftover ingredients.")

# Event Manager view
elif app_mode == "Event Manager":
    st.title("Event Planning & Management")
    
    tab1, tab2 = st.tabs(["Upcoming Events", "Plan New Event"])
    
    with tab1:
        st.subheader("Scheduled Events")
        
        if st.session_state.events:
            for i, event in enumerate(st.session_state.events):
                with st.expander(f"{event['name']} - {event['date']}"):
                    st.write(f"**Theme:** {event['theme']}")
                    st.write(f"**Guests:** {event['guests']}")
                    
                    st.write("**Menu:**")
                    for item in event['menu']:
                        st.write(f"- {item}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Edit", key=f"edit_{i}"):
                            st.session_state.edit_event_index = i
                    with col2:
                        if st.button("Delete", key=f"delete_{i}"):
                            st.session_state.events.pop(i)
                            st.success("Event deleted successfully!")
                            st.rerun()
        else:
            st.info("No upcoming events. Use the 'Plan New Event' tab to create one.")
    
    with tab2:
        st.subheader("Plan a New Event")
        
        # Event details form
        event_name = st.text_input("Event Name")
        
        col1, col2 = st.columns(2)
        with col1:
            event_date = st.date_input("Event Date", datetime.now() + timedelta(days=14))
            event_theme = st.selectbox("Event Theme", 
                                      ["Mediterranean Cuisine", "Health & Wellness", 
                                       "Farm to Table", "Cultural Fusion", "Custom"])
            
            if event_theme == "Custom":
                event_theme = st.text_input("Enter Custom Theme")
        
        with col2:
            guest_count = st.number_input("Number of Guests", min_value=1, value=20)
        
        # Get AI suggestions
        if st.button("Get Suggestions"):
            if event_name and event_theme and guest_count > 0:
                with st.spinner("Generating event suggestions..." + (" with AI assistance" if gemini_model else "")):
                    event_suggestion = generate_event_suggestion_with_ai(guest_count, event_theme)
                    
                    st.subheader("Suggested Plan")
                    st.write(f"**Details:** {event_suggestion['theme_details']}")
                    st.write(f"**Estimated Cost:** {event_suggestion['estimated_cost']}")
                    st.write(f"**Planning Timeline:** {event_suggestion['preparation_time']}")
                    
                    st.write("**Menu Suggestions:**")
                    menu_items = event_suggestion['menu']
                    selected_menu = st.multiselect("Select Menu Items", menu_items, default=menu_items)
            else:
                st.warning("Please fill in all required fields")
        
        # Save event
        if st.button("Save Event"):
            if event_name and event_date and guest_count > 0:
                new_event = {
                    "name": event_name,
                    "date": event_date.strftime("%Y-%m-%d"),
                    "guests": guest_count,
                    "theme": event_theme,
                    "menu": selected_menu if 'selected_menu' in locals() else []
                }
                
                st.session_state.events.append(new_event)
                st.success("Event saved successfully!")
            else:
                st.warning("Please fill in all required fields")

# Menu Personalization view
elif app_mode == "Menu Personalization":
    st.title("Personalized Menu Recommendations")
    
    st.write("Get personalized menu recommendations based on dietary preferences")
    
    # Dietary preferences
    preferences = st.multiselect(
        "Select dietary preferences",
        ["Vegetarian", "Vegan", "Gluten-Free", "Dairy-Free", "Keto", "High-Protein"]
    )
    
    # Health goals
    health_goals = st.multiselect(
        "Select health goals (optional)",
        ["Weight Management", "Energy Boost", "Digestive Health", "Heart Health", "General Wellness"]
    )
    
    # Generate recommendations
    if st.button("Get Recommendations"):
        with st.spinner("Analyzing your preferences..." + (" with AI assistance" if gemini_model else "")):
            if gemini_model and (preferences or health_goals):
                try:
                    # Create a prompt for Gemini
                    prompt = f"""
                    Create personalized menu recommendations based on these dietary preferences: {', '.join(preferences) if preferences else 'None'} 
                    and health goals: {', '.join(health_goals) if health_goals else 'None'}.
                    
                    Provide 3 dish recommendations with the following details for each:
                    1. Dish name
                    2. Brief description
                    3. Key benefits related to the preferences/goals
                    4. Customization options
                    
                    Return the response as JSON with an array of dish objects.
                    """
                    
                    response = gemini_model.generate_content(prompt)
                    import json
                    try:
                        recommendations = json.loads(response.text)
                        
                        st.subheader("Your Personalized AI Recommendations")
                        for dish in recommendations:
                            st.write(f"### {dish.get('name', 'Recommended Dish')}")
                            st.write(dish.get('description', ''))
                            st.write(f"**Benefits:** {dish.get('benefits', '')}")
                            
                            if 'customization' in dish:
                                st.write("**Customization Options:**")
                                for option in dish.get('customization', []):
                                    st.write(f"- {option}")
                            
                            st.write("---")
                        
                    except (json.JSONDecodeError, ValueError):
                        # Fallback to the original function
                        generate_menu_recommendations_fallback(preferences, health_goals)
                        
                except Exception as e:
                    # Fallback to the original function
                    generate_menu_recommendations_fallback(preferences, health_goals)
            else:
                # Use the original function
                generate_menu_recommendations_fallback(preferences, health_goals)

def generate_menu_recommendations_fallback(preferences, health_goals):
    """Original menu recommendation function"""
    # Define menu options based on preferences
    menu_options = {
        "Vegetarian": ["Mediterranean Grain Bowl", "Buddha Bowl", "Avocado Toast", "Quinoa Salad"],
        "Vegan": ["Acai Bowl", "Black Bean Bowl", "Roasted Vegetable Medley", "Falafel Plate"],
        "Gluten-Free": ["Grilled Salmon", "Berry Yogurt Parfait", "Sweet Potato Bowl", "Herb Chicken"],
        "Dairy-Free": ["Black Bean Bowl", "Lentil Soup", "Herb Fish", "Veggie Stir-Fry"],
        "Keto": ["Herb Chicken", "Grilled Salmon", "Avocado Egg Plate", "Greek Salad"],
        "High-Protein": ["Grilled Chicken", "Salmon", "Protein Bowl", "Egg Wrap"]
    }
    
    # Find dishes that match preferences
    matching_dishes = []
    if preferences:
        for pref in preferences:
            if pref in menu_options:
                if not matching_dishes:
                    matching_dishes = menu_options[pref].copy()
                else:
                    # Find intersection of dishes that match all preferences
                    matching_dishes = [dish for dish in matching_dishes if dish in menu_options[pref]]
        
        # If no dishes match all preferences, show options for at least one preference
        if not matching_dishes:
            all_matches = []
            for pref in preferences:
                if pref in menu_options:
                    all_matches.extend(menu_options[pref])
            matching_dishes = list(set(all_matches))  # Remove duplicates
    else:
        # Default recommendations if no preferences selected
        popular_dishes = ["Quinoa Salad", "Grilled Chicken", "Acai Bowl", "Sweet Potato Bowl", "Grilled Salmon"]
        matching_dishes = popular_dishes
    
    # Display recommendations
    st.subheader("Your Personalized Recommendations")
    
    # Choose up to 3 random recommendations
    recommended_dishes = random.sample(matching_dishes, min(3, len(matching_dishes)))
    
    for dish in recommended_dishes:
        st.write(f"### {dish}")
        st.write(f"Perfect for: {', '.join(preferences) if preferences else 'Everyone'}")
        st.write("---")
    
    # Customization options based on preferences
    st.write("**Customization Options:**")
    if "Gluten-Free" in preferences:
        st.write("- Substitute with gluten-free grains")
    if "Dairy-Free" in preferences:
        st.write("- Dairy-free dressing options")
    st.write("- Adjust spice level to your preference")
    st.write("- Add extra protein or vegetables")

# If this is the main program
if __name__ == "__main__":
    # Add a footer
    st.markdown("---")
    st.markdown("FutureEats - Powered by Streamlit and Gemini 1.5 Pro")