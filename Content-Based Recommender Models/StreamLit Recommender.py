import streamlit as st
import pandas as pd

# Load the datasets
city_data = pd.read_csv('City.csv')
places_data = pd.read_csv('Places.csv')
# Merge city and places data
data = pd.merge(city_data, places_data, on='City')

# Streamlit UI
def main():
    st.title('Tourism Recommendation System')
    option = st.radio('Choose an option:', ('Cities', 'Places'))

    if option == 'Cities':
        st.subheader('Select a city:')
        city_name = st.selectbox('', city_data['City'])
        if st.button('Recommend'):
            city_places = data[data['City'] == city_name]
            st.subheader(f'Places to visit in {city_name}:')
            for idx, place in city_places.iterrows():
                st.write('- Place:', place['Place'])
                st.write('  Distance from city center:', place['Distance'])
                st.write('  Ratings:', place['Rating'])
                st.write('  Place description:', place['Place_desc'])

    elif option == 'Places':
        st.subheader('Select a category:')
        categories = data['Category'].unique()
        selected_category = st.selectbox('', categories)
        category_places = data[data['Category'] == selected_category]
        if st.button('Recommend'):
            st.subheader(f'Places in category "{selected_category}":')
            for idx, place in category_places.iterrows():
                st.write('- City:', place['City'])
                st.write('  Place:', place['Place'])
                st.write('  Distance from city center:', place['Distance'])
                st.write('  Ratings:', place['Rating'])
                st.write('  Place description:', place['Place_desc'])

if __name__ == "__main__":
    main()
