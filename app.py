
import streamlit as st
import csv
import os
from collections import Counter
import random

# Initialize session state for page navigation
if "page" not in st.session_state:
    st.session_state.page = "home"

# Backend Functions
def save_to_csv(recipe):
    """Saves a recipe to the CSV file."""
    file_exists = os.path.exists("recipes.csv")
    with open("recipes.csv", "a", newline="") as csvfile:
        fieldnames = ["Name", "Ingredients", "Steps", "Background"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()
        writer.writerow(recipe)

def load_recipes():
    """Loads all recipes from the CSV file."""
    if not os.path.exists("recipes.csv"):
        return []
    with open("recipes.csv", "r") as csvfile:
        reader = csv.DictReader(csvfile)
        return list(reader)

def consolidate_ingredients(selected_recipes):
    """Consolidates ingredients and counts repeated items."""
    all_ingredients = []
    for recipe in selected_recipes:
        ingredients = recipe["Ingredients"].split(",")  # Assuming comma-separated ingredients
        ingredients = [ingredient.strip() for ingredient in ingredients]
        all_ingredients.extend(ingredients)

    return Counter(all_ingredients)

# Page Navigation
def go_to_page(page):
    st.session_state.page = page

def format_steps(steps):
    """
    Splits the steps into new lines if they start with a number.
    Assumes steps are separated by some form of punctuation (e.g., period, semicolon).
    """
    import re
    # Match parts of the string that start with a number followed by a dot or space
    step_lines = re.split(r'(?<=\d)\.\s*', steps)  
    formatted_steps = "\n".join([f"{i+1}. {step.strip()}" for i, step in enumerate(step_lines) if step.strip()])
    return formatted_steps

# Apply Custom CSS
def apply_custom_css():
    st.markdown("""
    <style>
    .block-container {
        padding: 1rem 2rem;  /* Adjust padding as needed */
    }
    .stButton > button {
        width: 100%;  /* Make buttons align and occupy full column width */
    }
    </style>
    """, unsafe_allow_html=True)

# Pages
def home_page():
    apply_custom_css()  # Apply CSS for better styling

    st.title("Namaste, Foodie")
    st.subheader("Reviving Traditions, One Recipe at a Time!")

    # Search bar and Add Recipe button with padding
    search_query = st.text_input("Search for Recipes", placeholder="Enter a recipe name...")
    if st.button("Search"):
        recipes = load_recipes()
        matching_recipes = [
            recipe for recipe in recipes if search_query.lower() in recipe["Name"].lower()
        ]

        if matching_recipes:
            for recipe in matching_recipes:
                st.subheader(recipe["Name"])
                st.write(f"*Ingredients:* {recipe['Ingredients']}")
                # Format steps to handle numbered steps
                steps = recipe['Steps']
                formatted_steps = format_steps(steps)
                st.write(f"*Steps:* {formatted_steps}")
                st.write(f"*Cultural Background:* {recipe['Background']}")
                st.write("---")
        else:
            st.info("No matching recipes found.")

    st.write("")  # Padding
    if st.button("ADD RECIPE", key="add_recipe_button"):
        go_to_page("add_recipe")

    # Today's Specials Section
    st.subheader("Today's Specials")
    recipes = load_recipes()
    if recipes:
        i = random.randint(0, len(recipes) - 1)
        random_recipe = recipes[i]
        st.markdown(f"""
        **{random_recipe['Name']}**
        - **Ingredients:** {random_recipe['Ingredients']}
        - **Steps:** {random_recipe['Steps']}
        - **Background:** {random_recipe['Background']}
        """)
    else:
        st.write("No recipes available yet!")

    # Categories Section
    st.subheader("Categories")
    col1, col2, col3 = st.columns([1, 1, 1])  # Equal column widths

    with col1:
        if st.button("Nani's Secrets", key="nani_secrets"):
            go_to_page("nani_secrets")
    with col2:
        if st.button("Shopping List Generator", key="shopping_list"):
            go_to_page("shopping_list")
    with col3:
        if st.button("Other Categories"):
            st.warning("More categories coming soon!")

def add_recipe_page():
    st.title("Add Your Recipe")
    with st.form("add_recipe_form"):
        name = st.text_input("Recipe Name")
        ingredients = st.text_area("Ingredients (comma-separated)")
        steps = st.text_area("Steps")
        background = st.text_area("Background/Story")
        submitted = st.form_submit_button("Submit Recipe")

        if submitted:
            if name and ingredients and steps and background:
                recipe = {
                    "Name": name,
                    "Ingredients": ingredients,
                    "Steps": steps,
                    "Background": background,
                }
                save_to_csv(recipe)
                st.success("Recipe added successfully!")
                go_to_page("home")
            else:
                st.error("Please fill out all fields!")

    if st.button("Back to Home"):
        go_to_page("home")

def nani_secrets_page():
    st.title("Nani's Secrets")
    st.markdown("""
    ### Timeless Tips from Nani's Kitchen:
    - **Spices:** Roast spices to enhance flavor and aroma.
    - **Preservation:** Store herbs in damp towels to keep them fresh.
    - **Rotis:** Add yogurt to your dough for softer, fluffier rotis.
    - **Soups:** Use vegetable scraps to make delicious broths.
    """)
    if st.button("Back to Home"):
        go_to_page("home")

def shopping_list_page():
    st.title("Shopping List Generator")
    recipes = load_recipes()

    if not recipes:
        st.warning("No recipes available! Please add some first.")
        if st.button("Back to Home"):
            go_to_page("home")
        return

    # Recipe selection
    selected_recipe_names = st.multiselect(
        "Select Recipes to Generate a Shopping List:",
        options=[recipe["Name"] for recipe in recipes],
    )
    selected_recipes = [
        recipe for recipe in recipes if recipe["Name"] in selected_recipe_names
    ]

    if st.button("Generate Shopping List"):
        if not selected_recipes:
            st.error("Please select at least one recipe!")
        else:
            consolidated = consolidate_ingredients(selected_recipes)

            st.subheader("Consolidated Shopping List:")
            for ingredient, count in consolidated.items():
                st.write(f"- {ingredient}: {count} Portions")

            # Download button
            shopping_list_data = "\n".join(
                [f"{ingredient}: {count}" for ingredient, count in consolidated.items()]
            )
            st.download_button(
                label="Download Shopping List",
                data=shopping_list_data,
                file_name="shopping_list.txt",
                mime="text/plain",
            )

    # Sustainability and Theme Additions
    st.markdown("### Sustainable Tips:")
    st.write("- **Reduce Waste:** Store unused ingredients for later.")
    st.write("- **Buy Locally:** Support farmers by choosing fresh, local produce.")
    st.write("- **Smart Substitutes:** Use alternatives like jaggery for sugar or coconut oil instead of butter.")

    if st.button("Back to Home"):
        go_to_page("home")

# Routing Pages
if st.session_state.page == "home":
    home_page()
elif st.session_state.page == "add_recipe":
    add_recipe_page()
elif st.session_state.page == "nani_secrets":
    nani_secrets_page()
elif st.session_state.page == "shopping_list":
    shopping_list_page()
