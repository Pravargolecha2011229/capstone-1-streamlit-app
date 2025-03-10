import streamlit as st
import pandas as pd
import random
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(
    page_title="FutureEats - Smart Restaurant Management",
    page_icon="🍽️",
    layout="wide"
)

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

# Helper functions
def generate_recipe_suggestion(ingredients):
    """Generate a recipe based on selected ingredients"""
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

def generate_event_suggestion(guest_count, theme):
    """Generate event planning suggestions"""
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
            with st.spinner("Creating your recipe..."):
                recipe = generate_recipe_suggestion(selected_ingredients)
            
            st.subheader(recipe["name"])
            
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Ingredients:**")
                for ingredient in recipe["ingredients"]:
                    st.write(f"- {ingredient.title()}")
                
                st.write(f"**Preparation Time:** {recipe['preparation_time']}")
            
            with col2:
                st.write("**Nutritional Information:**")
                st.write(f"Calories: {recipe['nutrition']['calories']} kcal")
                st.write(f"Protein: {recipe['nutrition']['protein']}g")
                st.write(f"Carbs: {recipe['nutrition']['carbs']}g")
            
            st.write("**Instructions:**")
            for i, step in enumerate(recipe["instructions"]):
                st.write(f"{i+1}. {step}")
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
                with st.spinner("Finding recipes for your leftovers..."):
                    recipe = generate_recipe_suggestion(st.session_state.leftovers)
                    
                    st.write(f"### {recipe['name']}")
                    st.write("A perfect way to use your leftover ingredients!")
                    
                    st.write("**Ingredients needed:**")
                    for ingredient in recipe['ingredients']:
                        st.write(f"- {ingredient.title()}")
                    
                    st.write("**Quick Instructions:**")
                    for i, step in enumerate(recipe["instructions"]):
                        st.write(f"{i+1}. {step}")
                    
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
                with st.spinner("Generating event suggestions..."):
                    event_suggestion = generate_event_suggestion(guest_count, event_theme)
                    
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
        with st.spinner("Analyzing your preferences..."):
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