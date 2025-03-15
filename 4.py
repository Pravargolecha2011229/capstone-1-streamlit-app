import streamlit as st
import pandas as pd
import random
from datetime import datetime, timedelta
import google.generativeai as genai
import plotly.express as px
import plotly.graph_objects as go

# Page configuration
st.set_page_config(
    page_title="FutureEats - Smart Restaurant Management",
    page_icon="🍽️",
    layout="wide"
)

# Configure Gemini API
GEMINI_API_KEY = "AIzaSyB5vTHMOf-4c6I5Z2T43dbXtW106mhDpVA"
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-pro')

# Quiz Questions Database
COOKING_QUIZ = [
    {
        "question": "What temperature is considered safe for cooking chicken?",
        "options": ["145°F", "165°F", "175°F", "185°F"],
        "correct": "165°F"
    },
    {
        "question": "Which herb is commonly used in Italian cuisine?",
        "options": ["Basil", "Lemongrass", "Cumin", "Cardamom"],
        "correct": "Basil"
    },
    {
        "question": "What is the main ingredient in traditional guacamole?",
        "options": ["Tomatoes", "Avocado", "Onions", "Lime"],
        "correct": "Avocado"
    },
    {
        "question": "Which cooking method involves cooking food in hot oil?",
        "options": ["Braising", "Steaming", "Frying", "Roasting"],
        "correct": "Frying"
    },
    {
        "question": "What is the process of partially cooking food in boiling water and then quickly cooling it in ice water?",
        "options": ["Sautéing", "Blanching", " Braising", "Roasting"],
        "correct": "Blanching"
    },
    {
        "question": "Which ingredient makes baked goods rise?",
        "options": ["Sugar", "Flour", "Salt", "Baking soda"],
        "correct": "Baking soda"
    },
   {
        "question": "What does 'tempering' mean when working with chocolate?",
        "options": ["Heating and cooling chocolate to stabilize it", " Mixing chocolate with milk", "Melting chocolate over direct heat", " Adding sugar to chocolate"],
        "correct": "Heating and cooling chocolate to stabilize it"
    },
    {
        "question": "Which country is known for originating sushi?",
        "options": ["China", "Korea", "Japan","Thailand"],
        "correct": "Japan"
    },
    {
        "question": "What is the main ingredient in hummus?",
        "options": ["Lentils", "Chickpeas", "Black beans","Peanuts"],
        "correct": "Chickpeas"
    },
    {
        "question": "What does 'sous vide' mean in cooking?",
        "options": ["Cooking with steam", "Cooking food in a vaccum-sealed bag in water", "Cooking over an open flame","Cooking in a pressure cooker"],
        "correct": "Cooking food in a vaccum-sealed bag in water"
    },
    {
        "question": "Which kitchen tool is best for zesting a lemon?",
        "options": ["Knife", "Peeler", "Grater","Microplane"],
        "correct": "Microplane"        
    },
    {
        "question": "What is the purpose of deglazing a pan?",
        "options": ["To remove excess fat", "To dissolve browned bits for added flavor", "To cool down the pan","To thicken a sauce"],
        "correct": " To dissolve browned bits for added flavor"        
    },
    {
        "question": "What does the term 'al dente' mean when cooking pasta?",
        "options": ["Soft and mushy", "Firm to the bite", "Overcooked","Undercooked"],
        "correct": "Firm to the bite"        
    },
    {
        "question": "What is the purpose of resting meat after cooking?",
        "options": ["To cool it down quickly", "To allow juices to redistribute", " To make it easier to cut","To enhance the flavor"],
        "correct": "To allow juices to redistribute"        
    },
    {
        "question": "What does the term 'proofing' mean in baking?",
        "options": ["Checking for quality", " Baking at a low temperature", "Mixing ingredients together","Allowing dough to rise"],
        "correct": "To allow juices to redistribute"        
    },
    {
        "question": "What type of sugar is commonly used in making caramel?",
        "options": ["Brown sugar", "Powdered sugar", "Granulated sugar","Coconut sugar"],
        "correct": "Granulated sugar"        
    },
    {
        "question": "Which type of rice is used to make sushi?",
        "options": ["Basmati rice", "Jasmine rice", "Arborio rice","Short-grain rice"],
        "correct": "Short-grain rice"        
    },
    {
        "question": "Which spice is commonly used in Indian cuisine and gives curry its yellow color?",
        "options": ["Saffron", "Paprika", "Turmeric","Cumin"],
        "correct": "Turmeric"        
    },
    {
        "question": "What is the purpose of 'searing' meat?",
        "options": ["To cook it completely", "To keep it cold", "To remove fat","To create a flavorful crust"],
        "correct": "To create a flavorful crust"        
    },
    {
        "question": "What is the French cooking term for 'everything in its place' (organizing ingredients before cooking)?",
        "options": ["Mise en place", "Sous vide", "En papillote","Bain-marie"],
        "correct": "Mise en place"        
    },
    {
        "question": "Which cooking method involves cooking food slowly in a covered pot with a small amount of liquid?",
        "options": ["Braising", "Sautéing", "Boiling","Grilling"],
        "correct": "Braising"        
    },
    {
        "question": "What gas is released when baking soda reacts with an acid?",
        "options": ["Oxygen", "Carbon dioxide", "Hydrogen","Nitrogen"],
        "correct": "Carbon dioxide"        
    },
    {
        "question": "What is the main ingredient in a traditional crème brûlée?",
        "options": ["Flour", "Cream", "Cheese","Butter"],
        "correct": "Cream"        
    },
    {
        "question": "What is the traditional flatbread of Mexico called?",
        "options": ["Tortilla", "Naam", "Roti","Bhature","Pita"],
        "correct": "Tortilla"        
    },
    {
        "question": "Which dish is traditionally made with fermented cabbage?",
        "options": ["Kimchi", "Sushi", "Falafel","Pasta"],
        "correct": "Kimchi"        
    },
    {
        "question": "What is the primary ingredient in a classic French béchamel sauce?",
        "options": ["Milk", "Cream", "Cheese","Butter"],
        "correct": "Milk"        
    },
    {
        "question": "What does 'basting' mean in cooking?",
        "options": ["Cooking with dry heat", "Pouring juices or melted fat over food while cooking", "Cooking food in a water bath","Cutting food into small pieces"],
        "correct": "Pouring juices or melted fat over food while cooking"        
    },
    {
        "question": "What is the term for cooking food in a tightly sealed pouch, usually with parchment paper or foil?",
        "options": ["En papillote", "Roasting", "Poaching","Braising"],
        "correct": "En papillote"        
    },
    {
        "question": "Which tool is best for checking the internal temperature of Water?",
        "options": ["Your hand", "Knife", "Tongs","Thermometer"],
        "correct": "Thermometer"        
    },
    {
        "question": "What is the best way to cut an onion without crying?",
        "options": ["Freeze the onion before cutting", "Use a dull knife", "Cut it under running water","Wear goggles"],
        "correct": "Freeze the onion before cutting"        
    },
    {
        "question": "Which of these dishes is traditionally cooked in a tandoor?",
        "options": ["Tacos", "Paella", "Naan","Sushi"],
        "correct": "Naan"        
    },
    {
        "question": "Which type of lentils are used to make traditional dal makhani?",
        "options": ["Moong dal", "Chana dal", "Masoor dal","Urad dal"],
        "correct": "Urad dal"    
    },
    {
        "question": "What spice gives biryani its distinctive yellow color?",
        "options": ["Saffron", "Turmeric", "Cumin","Spinach"],
        "correct": "Saffron"    
    },
    {
        "question": "What is the key ingredient in a traditional South Indian sambar?",
        "options": ["Chana dal", "Toor dal", "Rajma","Urad dal"],
        "correct": "Toor dal"    
    },
    {
        "question": "Which spice blend is commonly used in Indian chaat dishes?",
        "options": ["Garam Masala", "Chat Masala", "Rajma","Rasam Powder"],
        "correct": "Chat Masala"
    },
    {
        "question": "Which Indian dessert is made by deep-frying balls of khoya and soaking them in sugar syrup?",
        "options": ["Rasgulla", "Jalebi", "Barfi","Gulab Jamun,"],
        "correct": "Gulab Jamun"
    }

]

# Initialize session state
if 'recipe_database' not in st.session_state:
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
    st.session_state.inventory = {
        "vegetables": ["spinach", "kale", "carrots", "bell peppers", "cucumber", "tomatoes"],
        "proteins": ["chicken breast", "salmon", "tofu", "eggs", "chickpeas"],
        "grains": ["quinoa", "brown rice", "bread", "oats"],
        "fruits": ["apples", "bananas", "berries", "mango", "avocado", "lemon"]
    }

if 'leftovers' not in st.session_state:
    st.session_state.leftovers = ["spinach", "quinoa", "tomatoes"]

if 'user_points' not in st.session_state:
    st.session_state.user_points = 0

if 'activity_log' not in st.session_state:
    st.session_state.activity_log = []

if 'events' not in st.session_state:
    st.session_state.events = [
        {
            "name": "Corporate Lunch",
            "date": "2024-03-20",
            "guests": 50,
            "theme": "Mediterranean",
            "dietary_restrictions": ["Vegetarian", "Gluten-Free"],
            "status": "Upcoming"
        }
    ]    

# Helper Functions
def get_recipe_from_gemini(ingredients, dietary_restrictions=None):
    """Generate recipe using Gemini API"""
    prompt = f"Create a detailed recipe using these ingredients: {', '.join(ingredients)}"
    if dietary_restrictions:
        prompt += f"\nDietary restrictions: {', '.join(dietary_restrictions)}"
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Error generating recipe: {str(e)}")
        return None

def add_points(points, reason):
    """Add points and log activity"""
    st.session_state.user_points += points
    st.session_state.activity_log.append({
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "action": reason,
        "points": points
    })

def search_ingredients(search_term: str, ingredients_list: list) -> list:
    """Enhanced ingredient search with flexible matching and custom additions"""
    if not search_term:
        return ingredients_list

    search_term = search_term.lower()
    
    # Add searched term if not in list
    if search_term not in [i.lower() for i in ingredients_list]:
        ingredients_list.append(search_term.title())
    
    # Search with flexible matching
    matches = [
        item for item in ingredients_list 
        if search_term in item.lower() or 
        item.lower() in search_term or 
        any(word in item.lower() for word in search_term.split())
    ]
    
    return matches or [search_term.title()]

def get_all_ingredients():
    """Get all available ingredients across categories"""
    all_ingredients = []
    for category_items in st.session_state.inventory.values():
        all_ingredients.extend(category_items)
    return list(set(all_ingredients))

def suggest_recipes(ingredients, dietary_restrictions=None):
    """Generate recipe suggestions with enhanced prompting"""
    prompt = f"""Create a detailed recipe using these ingredients: {', '.join(ingredients)}
    Please include:
    - Recipe name
    - Preparation time
    - Cooking time
    - Difficulty level
    - Step by step instructions
    - Additional ingredients needed (if any)
    """
    if dietary_restrictions:
        prompt += f"\nMust be suitable for: {', '.join(dietary_restrictions)}"
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Error generating recipe: {str(e)}")
        return None

# Sidebar
st.sidebar.title("🍽️ FutureEats")
st.sidebar.header("Restaurant Management")

# Points Display
st.sidebar.markdown(f"### 🏆 Points: {st.session_state.user_points}")

# Navigation
app_mode = st.sidebar.selectbox(
    "Select Feature", 
    ["Dashboard", "Recipe Suggestions", "Leftover Management", "Menu Personalization", "Event Manager","Cooking Quiz"]
)

# Main Content
if app_mode == "Dashboard":
    st.title("🍽️ FutureEats Dashboard")
    
    # Key Metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Points", st.session_state.user_points)
    with col2:
        st.metric("Recipes Created", len(st.session_state.recipe_database))
    with col3:
        st.metric("Ingredients Available", sum(len(v) for v in st.session_state.inventory.values()))

    # Menu Performance
    st.subheader("📊 Menu Performance")
    menu_df = st.session_state.recipe_database
    fig_feedback = px.bar(menu_df, x='dish', y='feedback', 
                         title='Dish Ratings',
                         color='feedback',
                         color_continuous_scale='viridis')
    st.plotly_chart(fig_feedback, use_container_width=True)

    # Activity Analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔝 Top Rated Dishes")
        top_dishes = menu_df.nlargest(3, 'feedback')
        st.dataframe(top_dishes[['dish', 'feedback']], hide_index=True)
    
    with col2:
        st.subheader("📦 Inventory Status")
        inventory_data = []
        for category, items in st.session_state.inventory.items():
            inventory_data.append({'Category': category, 'Count': len(items)})
        
        inventory_df = pd.DataFrame(inventory_data)
        fig_inventory = px.pie(inventory_df, values='Count', names='Category',
                             title='Inventory Distribution')
        st.plotly_chart(fig_inventory, use_container_width=True)

    # Recent Activity
    st.subheader("📈 Recent Activity")
    if st.session_state.activity_log:
        activity_df = pd.DataFrame(st.session_state.activity_log)
        activity_df['date'] = pd.to_datetime(activity_df['date'])
        
        # Activity Timeline
        fig_activity = px.line(activity_df, x='date', y='points',
                             title='Points Timeline',
                             markers=True)
        st.plotly_chart(fig_activity, use_container_width=True)
        
        # Recent Activities Table
        st.subheader("🎯 Latest Actions")
        recent_df = pd.DataFrame(reversed(st.session_state.activity_log[-5:]))
        st.dataframe(recent_df, hide_index=True)


elif app_mode == "Recipe Suggestions":
    st.title("Recipe Suggestions")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        search_term = st.text_input("🔍 Search or add ingredients", key="recipe_search",
                                  help="Type any ingredient - it will be added if not found")
    with col2:
        show_categories = st.checkbox("Show categories", value=False)
    
    # Get and filter ingredients
    all_ingredients = get_all_ingredients()
    if search_term:
        filtered_ingredients = search_ingredients(search_term, all_ingredients)
    else:
        filtered_ingredients = all_ingredients
    
    if show_categories:
        category = st.selectbox("Filter by category", list(st.session_state.inventory.keys()))
        filtered_ingredients = [i for i in filtered_ingredients if i in st.session_state.inventory[category]]
    
    selected_ingredients = st.multiselect(
        "Selected Ingredients",
        options=sorted(filtered_ingredients),
        default=[search_term.title()] if search_term else [],
        key="recipe_ingredients"
    )
    
    if st.button("Generate Recipe", type="primary"):
        if selected_ingredients:
            with st.spinner("Creating your recipe..."):
                recipe = suggest_recipes(selected_ingredients)
                if recipe:
                    st.success("Recipe generated successfully!")
                    st.write(recipe)
                    add_points(5, "Generated new recipe")
        else:
            st.warning("Please select ingredients first")



elif app_mode == "Leftover Management":
    st.title("Leftover Management")
    
    search_term = st.text_input("🔍 Search or add leftover ingredients", 
                               key="leftover_search",
                               help="Type any ingredient - it will be added if not found")
    
    all_ingredients = get_all_ingredients()
    if search_term:
        filtered_ingredients = search_ingredients(search_term, all_ingredients)
    else:
        filtered_ingredients = all_ingredients
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Available Ingredients")
        leftover_items = st.multiselect(
            "Select ingredients",
            options=sorted(filtered_ingredients),
            default=[search_term.title()] if search_term else [],
            key="leftover_ingredients"
        )
    
    with col2:
        st.subheader("Recipe Suggestions")
        if st.button("Get Recipe Ideas", type="primary"):
            if leftover_items:
                with st.spinner("Creating recipe from leftovers..."):
                    recipe = suggest_recipes(leftover_items)
                    if recipe:
                        st.success("Recipe generated successfully!")
                        st.write(recipe)
                        add_points(5, "Generated leftover recipe")
            else:
                st.warning("Please select ingredients first")


elif app_mode == "Menu Personalization":
    st.title("Personalized Menu Recommendations")
    
    # Dietary preferences with search
    st.subheader("Dietary Preferences")
    pref_search = st.text_input("🔍 Search preferences", key="pref_search")
    all_preferences = [
        "Vegetarian", "Vegan", "Gluten-Free", "Dairy-Free", "Keto", 
        "High-Protein", "Low-Carb", "Mediterranean", "Paleo", "Pescatarian"
    ]
    
    if pref_search:
        filtered_preferences = search_ingredients(pref_search, all_preferences)
    else:
        filtered_preferences = all_preferences
    
    preferences = st.multiselect(
        "Select preferences",
        options=sorted(filtered_preferences),
        default=[pref_search.title()] if pref_search else [],
        key="diet_preferences"
    )
    
    # Custom ingredients with search
    st.subheader("Additional Ingredients")
    ingredient_search = st.text_input("🔍 Search or add specific ingredients", key="menu_ingredients")
    
    all_ingredients = get_all_ingredients()
    if ingredient_search:
        filtered_ingredients = search_ingredients(ingredient_search, all_ingredients)
    else:
        filtered_ingredients = all_ingredients
    
    selected_ingredients = st.multiselect(
        "Select ingredients",
        options=sorted(filtered_ingredients),
        default=[ingredient_search.title()] if ingredient_search else [],
        key="menu_ingredients_select"
    )
    
    if st.button("Generate Personalized Menu", type="primary"):
        if preferences or selected_ingredients:
            with st.spinner("Creating personalized menu..."):
                recipe = suggest_recipes(selected_ingredients, preferences)
                if recipe:
                    st.success("Menu generated successfully!")
                    st.write(recipe)
                    add_points(5, "Generated personalized menu")
        else:
            st.warning("Please select at least one preference or ingredient")
            
elif app_mode == "Event Manager":
    st.title("🎉 Event Manager")
    
    # Create tabs for different event management functions
    tab1, tab2, tab3 = st.tabs(["Create Event", "View Events", "Event Analytics"])
    
    with tab1:
        st.subheader("Plan New Event")
        
        col1, col2 = st.columns(2)
        with col1:
            event_name = st.text_input("Event Name")
            event_date = st.date_input("Event Date")
            guest_count = st.number_input("Number of Guests", min_value=2, value=20)
        
        with col2:
            event_theme = st.selectbox("Event Theme", 
                ["Mediterranean", "Asian Fusion", "Traditional", "Modern American", 
                 "Indian", "Mexican", "Italian", "Casual Buffet"])
            
            dietary_restrictions = st.multiselect(
                "Dietary Restrictions",
                ["Vegetarian", "Vegan", "Gluten-Free", "Dairy-Free", 
                 "Nut-Free", "Halal", "Kosher"]
            )
        
        # Menu Planning
        st.subheader("Menu Planning")
        courses = ["Appetizers", "Main Course", "Desserts", "Beverages"]
        menu_items = {}
        
        for course in courses:
            st.write(f"**{course}**")
            col1, col2 = st.columns(2)
            
            with col1:
                # Get suggestions based on theme and restrictions
                if st.button(f"Get {course} Suggestions"):
                    with st.spinner("Generating suggestions..."):
                        prompt = f"""Suggest 3 {course.lower()} for a {event_theme} themed event with {guest_count} guests.
                        Must accommodate these dietary restrictions: {', '.join(dietary_restrictions) if dietary_restrictions else 'None'}
                        Include brief descriptions."""
                        
                        suggestions = get_recipe_from_gemini([], dietary_restrictions)
                        if suggestions:
                            st.write(suggestions)
                            add_points(2, f"Generated {course.lower()} suggestions")
            
            with col2:
                menu_items[course] = st.text_area(f"Selected {course}", height=100,
                    placeholder=f"Enter selected {course.lower()} here...")
        
        # Cost Estimation
        st.subheader("Cost Estimation")
        per_person_cost = st.number_input("Estimated Cost per Person (₹)", min_value=200.0, value=250.0)
        total_cost = per_person_cost * guest_count
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Estimated Cost", f"₹{total_cost:,.2f}")
        with col2:
            st.metric("Cost per Person", f"₹{per_person_cost:.2f}")
        with col3:
            st.metric("Total Guests", guest_count)
        
        # Save Event
        if st.button("Save Event"):
            if event_name and event_date:
                new_event = {
                    "name": event_name,
                    "date": event_date.strftime("%Y-%m-%d"),
                    "guests": guest_count,
                    "theme": event_theme,
                    "dietary_restrictions": dietary_restrictions,
                    "menu": menu_items,
                    "cost_per_person": per_person_cost,
                    "total_cost": total_cost,
                    "status": "Upcoming"
                }
                
                st.session_state.events.append(new_event)
                st.success("Event saved successfully!")
                add_points(10, f"Created new event: {event_name}")
            else:
                st.error("Please fill in event name and date")
    
    with tab2:
        st.subheader("Upcoming Events")
        
        if not st.session_state.events:
            st.info("No events planned yet")
        else:
            for idx, event in enumerate(st.session_state.events):
                with st.expander(f"{event['date']} - {event['name']}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Theme:** {event['theme']}")
                        st.write(f"**Guests:** {event['guests']}")
                        st.write(f"**Status:** {event['status']}")
                    
                    with col2:
                        st.write("**Dietary Restrictions:**")
                        for restriction in event['dietary_restrictions']:
                            st.write(f"- {restriction}")
                    
                    if 'menu' in event:
                        st.write("**Menu:**")
                        for course, items in event['menu'].items():
                            if items.strip():  # Only show if items were added
                                st.write(f"*{course}:*")
                                st.write(items)
                    
                    # Event actions
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"Mark Complete {idx}"):
                            st.session_state.events[idx]['status'] = "Completed"
                            st.rerun()
                    with col2:
                        if st.button(f"Delete Event {idx}"):
                            st.session_state.events.pop(idx)
                            st.rerun()
    
    with tab3:
        st.subheader("Event Analytics")
        
        if not st.session_state.events:
            st.info("No events data available")
        else:
            # Convert events to DataFrame for analysis
            events_df = pd.DataFrame(st.session_state.events)
            
            # Event count by theme
            fig_themes = px.pie(events_df, names='theme', title='Events by Theme')
            st.plotly_chart(fig_themes, use_container_width=True)
            
            # Guest distribution
            fig_guests = px.box(events_df, y='guests', title='Guest Count Distribution')
            st.plotly_chart(fig_guests, use_container_width=True)
            
            # Cost analysis
            if 'total_cost' in events_df.columns:
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total Revenue", f"${events_df['total_cost'].sum():,.2f}")
                with col2:
                    st.metric("Average Event Cost", 
                             f"₹{events_df['total_cost'].mean():,.2f}")

elif app_mode == "Cooking Quiz":
    st.title("👨‍🍳 Cooking Knowledge Quiz")
    st.write("Test your cooking knowledge and earn points!")
    
    # Quiz Statistics
    if 'quiz_stats' not in st.session_state:
        st.session_state.quiz_stats = {
            'total_attempts': 0,
            'correct_answers': 0
        }
    
    # Display quiz statistics
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Attempts", st.session_state.quiz_stats['total_attempts'])
    with col2:
        accuracy = 0 if st.session_state.quiz_stats['total_attempts'] == 0 else \
                  (st.session_state.quiz_stats['correct_answers'] / st.session_state.quiz_stats['total_attempts']) * 100
        st.metric("Accuracy", f"{accuracy:.1f}%")
    
    # Quiz Interface
    if 'current_question' not in st.session_state:
        st.session_state.current_question = random.choice(COOKING_QUIZ)
    
    st.subheader("Question:")
    question = st.session_state.current_question
    st.write(question["question"])
    
    user_answer = st.radio("Select your answer:", question["options"], key="quiz_answer")
    
    if st.button("Submit Answer"):
        st.session_state.quiz_stats['total_attempts'] += 1
        
        if user_answer == question["correct"]:
            st.success("🎉 Correct! +5 points")
            add_points(5, "Correct quiz answer")
            st.session_state.quiz_stats['correct_answers'] += 1
        else:
            st.error(f"❌ Wrong answer. -1 point. Correct answer was: {question['correct']}")
            add_points(-1, "Wrong quiz answer")
        
        # Get new question
        new_questions = [q for q in COOKING_QUIZ if q != question]
        if new_questions:
            st.session_state.current_question = random.choice(new_questions)
        
        # Show continue button
        if st.button("Next Question"):
            st.rerun()