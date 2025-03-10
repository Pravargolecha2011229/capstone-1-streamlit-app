import streamlit as st
import pandas as pd
import openai

# Set up OpenAI API Key
openai.api_key = "AIzaSyBHf20B9RLgXxn0mhCSEhJWilRG6QhM_jk"  # Replace with actual API key

# Set up the page
st.set_page_config(page_title="Smart Restaurant AI", layout="wide")
st.title("🍽️ Smart Restaurant Management AI")

# Sidebar navigation
menu = st.sidebar.selectbox("Select a Feature", [
    "Menu & Inventory Management", "Leftover Tracking", "AI Recipe Suggestions"
])

# Sample DataFrame for menu & inventory
if "menu_df" not in st.session_state:
    data = {
        "Day": [1],
        "Dish Name": ["Vegan Stir Fry"],
        "Category": ["Main"],
        "Ingredients": ["Tofu, Bell peppers, Soy sauce"],
        "Diet Type": ["Vegan"],
        "Inventory Used": ["200g tofu, 3 bell peppers, 100ml soy sauce"],
        "Leftovers": ["50g tofu, 1 bell pepper"],
        "Consumption": ["150g tofu, 2 bell peppers"]
    }
    st.session_state.menu_df = pd.DataFrame(data)

if menu == "Menu & Inventory Management":
    st.header("📋 Menu & Inventory Management")
    st.dataframe(st.session_state.menu_df)
    
    with st.form("add_dish"):
        st.subheader("Add New Dish")
        day = st.number_input("Day", min_value=1, max_value=31, step=1)
        dish = st.text_input("Dish Name")
        category = st.selectbox("Category", ["Main", "Side", "Dessert"])
        ingredients = st.text_area("Ingredients")
        diet_type = st.selectbox("Diet Type", ["Vegan", "Gluten-Free", "Regular"])
        inventory_used = st.text_area("Inventory Used")
        leftovers = st.text_area("Leftovers")
        consumption = st.text_area("Consumption")
        submit = st.form_submit_button("Add Dish")
    
    if submit and dish:
        new_row = pd.DataFrame({
            "Day": [day], "Dish Name": [dish], "Category": [category],
            "Ingredients": [ingredients], "Diet Type": [diet_type],
            "Inventory Used": [inventory_used], "Leftovers": [leftovers],
            "Consumption": [consumption]
        })
        st.session_state.menu_df = pd.concat([st.session_state.menu_df, new_row], ignore_index=True)
        st.success("Dish Added Successfully!")

elif menu == "Leftover Tracking":
    st.header("🍱 Leftover Tracking")
    st.dataframe(st.session_state.menu_df[["Day", "Dish Name", "Leftovers"]])
    
    with st.form("update_leftover"):
        day = st.number_input("Day to Update", min_value=1, max_value=31, step=1)
        new_leftovers = st.text_area("Updated Leftovers")
        submit = st.form_submit_button("Update Leftovers")
    
    if submit and new_leftovers:
        st.session_state.menu_df.loc[st.session_state.menu_df["Day"] == day, "Leftovers"] = new_leftovers
        st.success("Leftovers Updated Successfully!")

elif menu == "AI Recipe Suggestions":
    st.header("🤖 AI Recipe Suggestions")
    ingredients_input = st.text_area("Enter Available Ingredients")
    generate = st.button("Generate Recipe")
    
    if generate and ingredients_input:
        prompt = f"Suggest a creative and delicious recipe using the following ingredients: {ingredients_input}. Provide step-by-step instructions."
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "system", "content": "You are a professional chef providing innovative recipes."},
                      {"role": "user", "content": prompt}]
        )
        recipe = response["choices"][0]["message"]["content"].strip()
        st.write(recipe)

st.sidebar.info("Built with Streamlit & AI-powered insights!")
