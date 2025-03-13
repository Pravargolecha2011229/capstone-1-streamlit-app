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

# Sidebar
st.sidebar.title("🍽️ FutureEats")
st.sidebar.header("Restaurant Management")

# Points Display
st.sidebar.markdown(f"### 🏆 Points: {st.session_state.user_points}")

# Navigation
app_mode = st.sidebar.selectbox(
    "Select Feature", 
    ["Dashboard", "Recipe Suggestions", "Leftover Management", "Menu Personalization", "Cooking Quiz"]
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
    
    categories = list(st.session_state.inventory.keys())
    selected_category = st.selectbox("Ingredient Category", categories)
    
    available_ingredients = st.session_state.inventory[selected_category]
    selected_ingredients = st.multiselect("Select Ingredients", available_ingredients)
    
    dietary_restrictions = st.multiselect(
        "Dietary Restrictions (optional)",
        ["Vegetarian", "Vegan", "Gluten-Free", "Dairy-Free"]
    )
    
    if st.button("Generate Recipe"):
        if selected_ingredients:
            with st.spinner("Creating your recipe..."):
                recipe = get_recipe_from_gemini(selected_ingredients, dietary_restrictions)
                if recipe:
                    st.write(recipe)
                    add_points(5, "Generated new recipe")
        else:
            st.warning("Please select ingredients first")

elif app_mode == "Leftover Management":
    st.title("Leftover Management")
    
    all_ingredients = update_leftovers()
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Current Leftovers")
        leftover_items = st.multiselect(
            "Select leftover ingredients",
            options=all_ingredients,
            default=[item for item in st.session_state.leftovers if item in all_ingredients]
        )
    
    with col2:
        st.subheader("Recipe Suggestions for Leftovers")
        if st.button("Get Recipe Ideas"):
            if leftover_items:
                with st.spinner("Generating recipe..."):
                    recipe = get_recipe_from_gemini(leftover_items)
                    if recipe:
                        st.write(recipe)
                        add_points(5, "Generated leftover recipe")
            else:
                st.warning("Please select leftover ingredients first")

elif app_mode == "Menu Personalization":
    st.title("Personalized Menu Recommendations")
    
    preferences = st.multiselect(
        "Select dietary preferences",
        ["Vegetarian", "Vegan", "Gluten-Free", "Dairy-Free", "Keto", "High-Protein"]
    )
    
    health_goals = st.multiselect(
        "Select health goals",
        ["Weight Management", "Energy Boost", "Digestive Health", "Heart Health"]
    )
    
    if st.button("Get Personalized Recipes"):
        if preferences or health_goals:
            with st.spinner("Generating personalized recommendations..."):
                recommendations = get_recipe_from_gemini([], preferences)
                if recommendations:
                    st.write(recommendations)
                    add_points(5, "Got personalized recommendations")
        else:
            st.warning("Please select at least one preference or health goal")

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