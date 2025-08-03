import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
import numpy as np

# Load the datasets
data = pd.read_csv('Final Dataset.csv')
hotels = pd.read_csv('Hotels.csv')
users = pd.read_csv('User.csv')

# Data Cleaning
data.drop_duplicates(subset=['City_Name', 'Place_Name'], inplace=True)
data.fillna({'Place_desc': '', 'Category': '', 'Best_time_to_visit': ''}, inplace=True)
hotels.fillna({'hotel_description': '', 'property_type': ''}, inplace=True)

# Feature Engineering for Places
places_content = data[['Place_Name', 'Place_desc', 'Category', 'Best_time_to_visit']].drop_duplicates()
places_content['combined_features'] = (
    places_content['Place_desc'] + ' ' + places_content['Category']
)

# Ensure unique Place_Name
places_content.drop_duplicates(subset=['Place_Name'], inplace=True)

# TF-IDF Vectorization
vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
tfidf_matrix = vectorizer.fit_transform(places_content['combined_features'])

# Cosine Similarity
content_similarity = cosine_similarity(tfidf_matrix)
content_similarity_df = pd.DataFrame(
    content_similarity, index=places_content['Place_Name'], columns=places_content['Place_Name']
)

# Ensure unique indices and columns for content_similarity_df
content_similarity_df = content_similarity_df.loc[~content_similarity_df.index.duplicated()]
content_similarity_df = content_similarity_df.loc[:, ~content_similarity_df.columns.duplicated()]

# Collaborative Filtering
rating_matrix = data.pivot_table(index='User_Id', columns='Place_Name', values='User_Rating').fillna(0)
rating_matrix = rating_matrix.loc[~rating_matrix.index.duplicated(), ~rating_matrix.columns.duplicated()]
normalized_ratings = rating_matrix.apply(lambda x: (x - x.mean()) / (x.std() + 1e-9), axis=1)
collab_similarity = cosine_similarity(normalized_ratings.T)
collab_similarity_df = pd.DataFrame(
    collab_similarity, index=rating_matrix.columns, columns=rating_matrix.columns
)

# Ensure unique indices and columns for collab_similarity_df
collab_similarity_df = collab_similarity_df.loc[~collab_similarity_df.index.duplicated()]
collab_similarity_df = collab_similarity_df.loc[:, ~collab_similarity_df.columns.duplicated()]

# Hybrid Recommendation Function
def hybrid_recommendation(place_name, user_rating, alpha=0.5):
    if place_name not in content_similarity_df.index or place_name not in collab_similarity_df.index:
        return None
    
    content_scores = content_similarity_df[place_name]
    collab_scores = collab_similarity_df[place_name]
    
    # Align indices
    aligned_index = content_scores.index.intersection(collab_scores.index)
    content_scores = content_scores.loc[aligned_index]
    collab_scores = collab_scores.loc[aligned_index]

    hybrid_scores = alpha * content_scores + (1 - alpha) * collab_scores
    return hybrid_scores.sort_values(ascending=False)

# Define age-based category mappings
teen_categories = {'Beaches', 'Valleys', 'Waterbodies', 'Trekking', 'Adventurous Trips'}
senior_categories = {'Temples', 'Hospitals', 'Forts', 'Tunnels'}


def recommend_places_by_city(city_name, selected_category, user_rating, alpha=0.5, user_id=None):
    # Fetch user's age if user_id is provided
    user_age = None
    if user_id is not None and user_id in users['User_ID'].values:
        user_age = users.loc[users['User_ID'] == user_id, 'Age'].values[0]
    
    city_places = data[data['City_Name'].str.lower() == city_name.lower()]
    
    # Always filter by the selected category if specified
    if selected_category and selected_category != 'Select a category':
        city_places = city_places[city_places['Category'] == selected_category]
    
    # If no places match the category, apply age-based filtering
    if city_places.empty and user_age is not None:
        if user_age < 40:
            city_places = city_places[city_places['Category'].isin(teen_categories)]
        else:
            city_places = city_places[city_places['Category'].isin(senior_categories)]
    
    # Handle no places found after filtering
    if city_places.empty:
        city_places = data[data['City_Name'].str.lower() == city_name.lower()]
    
    relevant_places = set(city_places['Place_Name']) & set(content_similarity_df.index)
    
    # If no relevant places, recommend popular places across all cities
    if not relevant_places:
        fallback_places = data.nlargest(10, 'User_Rating')
        return fallback_places[['Place_Name', 'Category', 'User_Rating', 'Place_desc']].drop_duplicates()
    
    recommendations = pd.Series(dtype='float32')
    for place in relevant_places:
        scores = hybrid_recommendation(place, user_rating, alpha)
        if scores is not None:
            recommendations = recommendations.add(scores, fill_value=0)
    
    # Exclude places already rated by the user
    if user_id is not None and user_id in rating_matrix.index:
        user_ratings = rating_matrix.loc[user_id]
        recommendations = recommendations[~recommendations.index.isin(user_ratings[user_ratings > 0].index)]
    
    recommendations = recommendations.sort_values(ascending=False).head(10)
    
    # Fallback to popular places if no personalized recommendations found
    if recommendations.empty:
        fallback_places = city_places.nlargest(10, 'User_Rating')
        return fallback_places[['Place_Name', 'Category', 'User_Rating', 'Place_desc']].drop_duplicates()
    
    return recommendations


# Recommend Hotels Function
def recommend_hotels(city, min_reviews=3):
    filtered = hotels[hotels['city'].str.lower() == city.lower()]
    filtered = filtered[filtered['site_review_rating'] >= min_reviews]
    
    if filtered.empty:
        # st.warning(f"No hotels found in {city}. Showing top-rated hotels globally.")
        fallback_hotels = hotels.nlargest(10, 'site_review_rating')
        return fallback_hotels[['Hotel_Name', 'hotel_description', 'hotel_star_rating', 'property_type']].drop_duplicates()
    
    filtered['review_score'] = MinMaxScaler().fit_transform(
        (0.5 * filtered['guest_recommendation'] +
         0.3 * filtered['site_review_rating'] +
         0.2 * filtered['hotel_star_rating']).values.reshape(-1, 1)
    )
    recommendations = filtered.sort_values(by='review_score', ascending=False).head(10)
    return recommendations

# Streamlit App
def main():
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

    st.title('Hybrid Tourism Recommendation System')

    # User input for city and category
    city_name = st.selectbox('Select a city:', options=['Select a city'] + list(data['City_Name'].unique()))
    selected_category = st.selectbox('Select a category:', options=['Select a category'] + list(data['Category'].unique()))

    # Fetch the user ID from session state
    user_id = st.session_state.get('user_id', None)

    # Recommendation for places based on button click
    if st.button('Recommend Places'):
        if city_name != 'Select a city':
            places = recommend_places_by_city(city_name, selected_category, user_rating=5, user_id=user_id)
            if places is None or places.empty:
                st.markdown('<p style="color:blue;">No recommendations available.</p>', unsafe_allow_html=True)
            else:
                st.markdown(f"<h3 style='color:#2e8b57;'>Place Recommendations:</h3>", unsafe_allow_html=True)
                for place_name in places.index:
                    place_details = data[data['Place_Name'] == place_name].iloc[0]
                    st.markdown(
                        f"""
                        <div class="card">
                            <h3>{place_name}</h3>
                            <p><b>Category:</b> {place_details['Category']}</p>
                            <p><b>Distance:</b> {place_details['Distance']}</p>
                            <p><b>Ratings:</b> {place_details['User_Rating']}</p>
                            <p><b>Description:</b> {place_details['Place_desc']}</p>
                            <p><b>Best Time to Visit:</b> {place_details['Best_time_to_visit']}</p>
                        </div>
                        """, unsafe_allow_html=True
                    )
        else:
            st.warning('Please select a city to proceed.')

    # Recommendation for hotels based on button click
    if st.button('Recommend Hotels'):
        if city_name != 'Select a city':
            recommended_hotels = recommend_hotels(city_name)
            if recommended_hotels.empty:
                st.markdown('<p style="color:blue;">No hotel recommendations available.</p>', unsafe_allow_html=True)
            else:
                st.markdown(f"<h3 style='color:#2e8b57;'>Hotel Recommendations:</h3>", unsafe_allow_html=True)
                for _, row in recommended_hotels.iterrows():
                    st.markdown(
                        f"""
                        <div class="card">
                            <h3>{row['Hotel_Name']}</h3>
                            <p><b>Description:</b> {row['hotel_description']}</p>
                            <p><b>Ratings:</b> {round(row['hotel_star_rating'])} stars</p>
                            <p><b>Type:</b> {row['property_type']}</p>
                            <p><b>Point Of Interest:</b> {row['point_of_interest']}</p>
                        </div>
                        """, unsafe_allow_html=True
                    )
        else:
            st.warning('Please select a city to proceed.')
    
    # Fallback to warnings or info if no input
    if city_name == 'Select a city' or selected_category == 'Select a category':
        st.markdown('<p style="color:blue;">Please select a city and category to get recommendations.</p>', unsafe_allow_html=True)

def recommender_page():
    # Check if user is logged in
    if 'user_id' not in st.session_state:
        st.warning("Please log in first.")
        st.stop()

    main()
    
    # Display the User ID message on the left
    user_id = st.session_state.get('user_id', 'Unknown')
    st.markdown(f"<b><center><span style='color: black;'>User ID: {user_id}</span></center></b>", unsafe_allow_html=True)

    # Display the logout button on the right
    if st.button("Logout", key="logout_button"):
        # Action for the logout button
        # You can replace this with logic to actually log the user out
        st.session_state.clear()  # Clear session data (e.g., user_id)
        st.experimental_rerun()  # Refresh the page
