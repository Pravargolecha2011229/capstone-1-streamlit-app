import streamlit as st
import pandas as pd
import datetime
import json
import os

# Set page configuration
st.set_page_config(page_title="Vegan Stir Fry Inventory Management", layout="wide")

# Application title and description
st.title("Vegan Stir Fry Inventory Management")
st.markdown("Track and manage your vegan stir fry ingredients inventory")

# Initialize session state variables if they don't exist
if 'inventory' not in st.session_state:
    st.session_state.inventory = {
        'vegetables': {},
        'proteins': {},
        'sauces': {},
        'grains': {}
    }
    
if 'history' not in st.session_state:
    st.session_state.history = []

# File paths for data persistence
INVENTORY_FILE = "vegan_inventory.json"
HISTORY_FILE = "inventory_history.json"

# Load existing data if available
def load_data():
    if os.path.exists(INVENTORY_FILE):
        with open(INVENTORY_FILE, 'r') as f:
            st.session_state.inventory = json.load(f)
    
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            st.session_state.history = json.load(f)

# Save data to files
def save_data():
    with open(INVENTORY_FILE, 'w') as f:
        json.dump(st.session_state.inventory, f)
    
    with open(HISTORY_FILE, 'w') as f:
        json.dump(st.session_state.history, f)

# Try to load existing data
try:
    load_data()
except Exception as e:
    st.warning(f"Could not load existing data: {e}")

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Inventory Management", "Add/Remove Items", "Usage History", "Recipes"])

# Function to add inventory history
def add_to_history(action, category, item, quantity, unit):
    st.session_state.history.append({
        'date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'action': action,
        'category': category,
        'item': item,
        'quantity': quantity,
        'unit': unit
    })
    save_data()

# Inventory Management Page
if page == "Inventory Management":
    st.header("Current Inventory")
    
    # Display inventory by category
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Vegetables")
        if st.session_state.inventory['vegetables']:
            veg_df = pd.DataFrame.from_dict(
                st.session_state.inventory['vegetables'], 
                orient='index',
                columns=['Quantity']
            ).reset_index()
            veg_df.columns = ['Item', 'Quantity']
            st.dataframe(veg_df, use_container_width=True)
        else:
            st.info("No vegetables in inventory")
            
        st.subheader("Proteins")
        if st.session_state.inventory['proteins']:
            proteins_df = pd.DataFrame.from_dict(
                st.session_state.inventory['proteins'], 
                orient='index',
                columns=['Quantity']
            ).reset_index()
            proteins_df.columns = ['Item', 'Quantity']
            st.dataframe(proteins_df, use_container_width=True)
        else:
            st.info("No proteins in inventory")
    
    with col2:
        st.subheader("Sauces")
        if st.session_state.inventory['sauces']:
            sauces_df = pd.DataFrame.from_dict(
                st.session_state.inventory['sauces'], 
                orient='index',
                columns=['Quantity']
            ).reset_index()
            sauces_df.columns = ['Item', 'Quantity']
            st.dataframe(sauces_df, use_container_width=True)
        else:
            st.info("No sauces in inventory")
            
        st.subheader("Grains")
        if st.session_state.inventory['grains']:
            grains_df = pd.DataFrame.from_dict(
                st.session_state.inventory['grains'], 
                orient='index',
                columns=['Quantity']
            ).reset_index()
            grains_df.columns = ['Item', 'Quantity']
            st.dataframe(grains_df, use_container_width=True)
        else:
            st.info("No grains in inventory")
    
    # Low stock alert
    st.subheader("Low Stock Alert")
    low_stock = []
    
    for category, items in st.session_state.inventory.items():
        for item, quantity in items.items():
            # Consider items with quantity less than 2 units as low stock
            if quantity < 2:
                low_stock.append({'Category': category, 'Item': item, 'Quantity': quantity})
    
    if low_stock:
        low_stock_df = pd.DataFrame(low_stock)
        st.dataframe(low_stock_df, use_container_width=True)
    else:
        st.success("All items are well-stocked!")

# Add/Remove Items Page
elif page == "Add/Remove Items":
    st.header("Add or Remove Items")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Add New Item")
        
        add_category = st.selectbox(
            "Select Category", 
            ["vegetables", "proteins", "sauces", "grains"],
            key="add_category"
        )
        
        add_item = st.text_input("Item Name", key="add_item")
        add_quantity = st.number_input("Quantity", min_value=0.1, value=1.0, step=0.1, key="add_quantity")
        add_unit = st.selectbox(
            "Unit", 
            ["kg", "g", "liter", "ml", "pcs", "bunch", "cup", "tbsp", "tsp", "bottle"],
            key="add_unit"
        )
        
        if st.button("Add Item"):
            if add_item:
                # Format the quantity with unit
                quantity_with_unit = f"{add_quantity} {add_unit}"
                
                st.session_state.inventory[add_category][add_item] = quantity_with_unit
                add_to_history("added", add_category, add_item, add_quantity, add_unit)
                st.success(f"Added {add_quantity} {add_unit} of {add_item} to {add_category}")
                save_data()
            else:
                st.error("Please enter an item name")
    
    with col2:
        st.subheader("Remove or Update Item")
        
        remove_category = st.selectbox(
            "Select Category", 
            ["vegetables", "proteins", "sauces", "grains"],
            key="remove_category"
        )
        
        # Get items from the selected category
        category_items = list(st.session_state.inventory[remove_category].keys())
        
        if category_items:
            remove_item = st.selectbox("Select Item", category_items, key="remove_item")
            current_quantity = st.session_state.inventory[remove_category][remove_item]
            st.write(f"Current quantity: {current_quantity}")
            
            action = st.radio("Action", ["Update Quantity", "Remove Item"], key="remove_action")
            
            if action == "Update Quantity":
                new_quantity = st.number_input("New Quantity", min_value=0.1, value=1.0, step=0.1, key="new_quantity")
                new_unit = st.selectbox(
                    "Unit", 
                    ["kg", "g", "liter", "ml", "pcs", "bunch", "cup", "tbsp", "tsp", "bottle"],
                    key="new_unit"
                )
                
                if st.button("Update"):
                    quantity_with_unit = f"{new_quantity} {new_unit}"
                    st.session_state.inventory[remove_category][remove_item] = quantity_with_unit
                    add_to_history("updated", remove_category, remove_item, new_quantity, new_unit)
                    st.success(f"Updated {remove_item} quantity to {new_quantity} {new_unit}")
                    save_data()
            else:
                if st.button("Remove"):
                    # Extract quantity and unit from the current value
                    parts = current_quantity.split()
                    if len(parts) >= 2:
                        quantity, unit = float(parts[0]), parts[1]
                    else:
                        quantity, unit = 0, ""
                        
                    del st.session_state.inventory[remove_category][remove_item]
                    add_to_history("removed", remove_category, remove_item, quantity, unit)
                    st.success(f"Removed {remove_item} from {remove_category}")
                    save_data()
        else:
            st.info(f"No items in {remove_category}")

# Usage History Page
elif page == "Usage History":
    st.header("Inventory Usage History")
    
    if st.session_state.history:
        history_df = pd.DataFrame(st.session_state.history)
        st.dataframe(history_df, use_container_width=True)
        
        # Download history as CSV
        csv = history_df.to_csv(index=False)
        st.download_button(
            label="Download History as CSV",
            data=csv,
            file_name="vegan_inventory_history.csv",
            mime="text/csv"
        )
        
        # Clear history option
        if st.button("Clear History"):
            st.session_state.history = []
            save_data()
            st.success("History cleared!")
            st.experimental_rerun()
    else:
        st.info("No history available")

# Recipes Page
elif page == "Recipes":
    st.header("Vegan Stir Fry Recipes")
    
    # Sample recipes
    recipes = {
        "Basic Vegetable Stir Fry": {
            "ingredients": {
                "vegetables": ["broccoli", "carrot", "bell pepper", "mushroom"],
                "proteins": ["tofu"],
                "sauces": ["soy sauce", "sesame oil"],
                "grains": ["rice"]
            },
            "instructions": """
            1. Press and cube tofu, then marinate in soy sauce
            2. Chop all vegetables into bite-sized pieces
            3. Heat a wok or large pan with oil
            4. Stir fry tofu until golden
            5. Add vegetables, starting with the firmest ones
            6. Add sauces and seasonings
            7. Serve over cooked rice
            """
        },
        "Spicy Peanut Stir Fry": {
            "ingredients": {
                "vegetables": ["red bell pepper", "snap peas", "onion", "carrot"],
                "proteins": ["tempeh"],
                "sauces": ["peanut butter", "sriracha", "soy sauce", "lime juice"],
                "grains": ["noodles"]
            },
            "instructions": """
            1. Slice tempeh and marinate in soy sauce
            2. Prepare peanut sauce by mixing peanut butter, sriracha, soy sauce, and lime juice
            3. Cook noodles according to package directions
            4. Stir fry tempeh until browned
            5. Add vegetables and stir fry until crisp-tender
            6. Add peanut sauce and toss to coat
            7. Serve over noodles and garnish with crushed peanuts
            """
        },
        "Teriyaki Vegetable Stir Fry": {
            "ingredients": {
                "vegetables": ["broccoli", "carrot", "snap peas", "mushroom"],
                "proteins": ["edamame"],
                "sauces": ["teriyaki sauce", "ginger", "garlic"],
                "grains": ["brown rice"]
            },
            "instructions": """
            1. Cook brown rice according to package directions
            2. Prepare vegetables by chopping into even pieces
            3. In a wok, sauté garlic and ginger
            4. Add vegetables, starting with carrots and broccoli
            5. Add edamame and continue stir frying
            6. Pour in teriyaki sauce and toss to coat
            7. Serve over brown rice and garnish with sesame seeds
            """
        }
    }
    
    # Recipe selector
    selected_recipe = st.selectbox("Select a Recipe", list(recipes.keys()))
    
    recipe = recipes[selected_recipe]
    
    # Display recipe
    st.subheader(selected_recipe)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Ingredients:**")
        
        for category, items in recipe["ingredients"].items():
            st.write(f"*{category.capitalize()}*")
            for item in items:
                # Check if item is in inventory
                if item in st.session_state.inventory[category]:
                    st.write(f"- {item} ✓")
                else:
                    st.write(f"- {item} ✗")
    
    with col2:
        st.write("**Instructions:**")
        st.write(recipe["instructions"])
    
    # Check if all ingredients are available
    all_available = True
    missing_items = []
    
    for category, items in recipe["ingredients"].items():
        for item in items:
            if item not in st.session_state.inventory[category]:
                all_available = False
                missing_items.append(f"{item} ({category})")
    
    if all_available:
        st.success("You have all the ingredients for this recipe!")
        
        if st.button("Make this recipe"):
            # Deduct ingredients from inventory
            for category, items in recipe["ingredients"].items():
                for item in items:
                    # Skip if item not in inventory (shouldn't happen if all_available is True)
                    if item not in st.session_state.inventory[category]:
                        continue
                    
                    # Extract quantity and unit from the current value
                    current = st.session_state.inventory[category][item]
                    parts = current.split()
                    if len(parts) >= 2:
                        quantity, unit = float(parts[0]), parts[1]
                    else:
                        quantity, unit = 0, ""
                    
                    # Deduct a standard amount (this is simplified, in a real app you'd have recipe quantities)
                    used_quantity = min(quantity, 0.5)  # Use up to 0.5 units
                    new_quantity = quantity - used_quantity
                    
                    if new_quantity <= 0:
                        del st.session_state.inventory[category][item]
                    else:
                        st.session_state.inventory[category][item] = f"{new_quantity} {unit}"
                    
                    add_to_history("used", category, item, used_quantity, unit)
            
            save_data()
            st.success("Recipe made! Inventory updated.")
    else:
        st.warning("You're missing some ingredients for this recipe:")
        for item in missing_items:
            st.write(f"- {item}")

# Add a shopping list generator
st.sidebar.markdown("---")
st.sidebar.subheader("Shopping List")

if st.sidebar.button("Generate Shopping List"):
    shopping_list = []
    
    # Add all low stock items
    for category, items in st.session_state.inventory.items():
        for item, quantity in items.items():
            parts = quantity.split()
            if len(parts) >= 2:
                qty, unit = float(parts[0]), parts[1]
            else:
                qty, unit = 0, ""
                
            if qty < 2:  # Low stock threshold
                shopping_list.append(f"{item} ({category}): Current: {qty} {unit}")
    
    # Display shopping list
    if shopping_list:
        st.sidebar.write("Items to buy:")
        for item in shopping_list:
            st.sidebar.write(f"- {item}")
    else:
        st.sidebar.write("All items are well-stocked!")