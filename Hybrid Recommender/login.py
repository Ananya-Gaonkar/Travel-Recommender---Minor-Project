import streamlit as st
import pandas as pd
import os

# File path for users data
USER_FILE_PATH = 'User.csv'

# Load user data with fallback
def load_users():
    if os.path.exists(USER_FILE_PATH):
        try:
            return pd.read_csv(USER_FILE_PATH)
        except Exception as e:
            st.error("Error loading user data: " + str(e))
            return pd.DataFrame(columns=['User_ID', 'User_Name', 'Email_Id', 'Age', 'Sex', 'Places_Visited', 'Ratings_Given'])
    else:
        # Return an empty DataFrame if the file does not exist
        return pd.DataFrame(columns=['User_ID', 'User_Name', 'Email_Id', 'Age', 'Sex', 'Places_Visited', 'Ratings_Given'])

# Save user data back to CSV
def save_users(users):
    users.to_csv(USER_FILE_PATH, index=False)

# Apply the theme to the page
st.markdown(
    """
    <style>
    .main {
        background-color: #f5f5f5;
        font-family: Arial, sans-serif;
    }
    h1 {
        color: #2e8b57;
        font-size: 2.5em;
        text-align: center;
        margin-bottom: 20px;
    }
    h2, h3 {
        color: #2e8b57;
        text-align: center;
        margin-bottom: 15px;
    }
    p {
        font-size: 1.2em;
        color: #333;
        text-align: justify;
        line-height: 1.6;
        margin-bottom: 10px;
    }
    .stButton > button:first-child {
    background-color: #4CAF50;
    color: white;
    font-size: 14px;
    padding: 8px 16px;
    border-radius: 5px;
    border: none;
    cursor: pointer;
    width: auto;
    margin: 5px auto;
    display: block;
    text-align: center;
    }
    .stButton > button:first-child:hover {
    background-color: #45a049;
    }
    .stSelectbox, .stTextInput {
        width: 100%;
        margin-bottom: 15px;
    }
    .stSelectbox select, .stTextInput input {
        font-size: 1.1em;
    }
    .stAlert {
        background-color: #f0f8ff;
        color: #1e90ff;
        padding: 10px;
        margin: 15px 0;
        border-radius: 5px;
        font-size: 1.1em;
    }
    .stWarning {
        background-color: #f0f8ff;
        color: #1e90ff;
        font-size: 1.2em;
    }
    .card {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        margin-bottom: 15px;
    }
    .card h3 {
        color: #2e8b57;
        font-size: 1.5em;
        margin-bottom: 10px;
    }
    .card p {
        font-size: 1.1em;
        margin: 5px 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Main login/registration logic
def login_page():
    st.title("Login or Register")

    # Load user data
    users = load_users()

    # Sidebar for login or registration
    option = st.radio("Choose an option", ["Login", "Register"], index=0)

    if option == "Login":
        st.subheader("Login")
        email = st.text_input("Enter your Email:")
        if st.button("Login"):
            if not users.empty and email.lower() in users['Email_Id'].str.lower().values:
                user_info = users[users['Email_Id'].str.lower() == email.lower()]
                st.success(f"Welcome, {user_info['User_Name'].values[0]}!")
                st.session_state['user_id'] = user_info['User_ID'].values[0]
                st.experimental_rerun()  # Navigate to recommender after login
            else:
                st.error("User not found. Please register.")
    
    elif option == "Register":
        st.subheader("Register")
        name = st.text_input("Enter your Name:")
        email = st.text_input("Enter your Email:")
        age = st.number_input("Enter your Age:", min_value=1, max_value=100, value=25)
        sex = st.selectbox("Select your Gender:", options=["Male", "Female", "Other"])
        places_visited = st.text_area(
            "Enter places you've visited (comma-separated):", 
            placeholder="e.g., Taj Mahal, Eiffel Tower"
        )
        ratings_given = st.slider(
            "Rate your overall travel experience (1-5):",
            min_value=1,
            max_value=5,
            value=0
        )

        # If no value is provided for places visited or ratings given, set them to empty
        if not places_visited:
            places_visited = None  # or you can use an empty string if preferred
        if ratings_given == 0:
            ratings_given = None  # or you can set this to an empty value or any other default behavior

        if st.button("Submit Registration"):
            if name and email and sex:
                if not users.empty and email.lower() in users['Email_Id'].str.lower().values:
                    st.warning("Email already exists. Please log in.")
                else:
                    new_user_id = users['User_ID'].max() + 1 if not users.empty else 1
                    new_user = pd.DataFrame([[
                        new_user_id, name, email, age, sex, places_visited, ratings_given
                    ]], columns=['User_ID', 'User_Name', 'Email_Id', 'Age', 'Sex', 'Places_Visited', 'Ratings_Given'])
                    
                    users = pd.concat([users, new_user], ignore_index=True)
                    save_users(users)  # Save updated users
                    st.success(f"Registration successful! Your User ID is {new_user_id}.")
            else:
                st.error("Please fill all required fields to register.")
