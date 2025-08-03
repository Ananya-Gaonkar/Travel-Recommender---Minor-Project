import streamlit as st
from login import login_page
from recommender import recommender_page

# Streamlit Session State for Navigation
if 'page' not in st.session_state:
    st.session_state['page'] = 'Login'

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

# Navigation
if st.session_state['page'] == 'Login':
    login_page()
    if 'user_id' in st.session_state:  # If login is successful
        st.session_state['page'] = 'Recommender'
        st.experimental_rerun()

elif st.session_state['page'] == 'Recommender':
    recommender_page()
