import pickle
import numpy as np
import streamlit as st
from streamlit_option_menu import option_menu
import requests
from PIL import Image
import sklearn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

# <---------------------------------------------------------- Page Configaration ----------------------------------------------------------------------------->
im = Image.open('MRS.jpeg')
st.set_page_config(layout="wide",page_title="Movie Recommender System",page_icon = im)

# <================================== For the main header ================================================================>
st.markdown(
    """
    <div style="background-color: #FF8C00 ; padding: 10px">
        <h1 style="color: brown; font-size: 48px; font-weight: bold">
           <center> <span style="color: black; font-size: 64px">M</span>ovie <span style="color: black; font-size: 64px">R</span>ecommender <span style="color: black; font-size: 64px">S</span>ystem</center>
        </h1>
    </div>
    """,
    unsafe_allow_html=True
)

# <=========================================================== Sidebar ================================================================================> 
with st.sidebar:
    st.title('''Movie Recommender 📺''')
    
    st.markdown('''
    ## About~
    This app has been developed by 2 students of VIT-AP :\n
    Arya Chakraborty [22MSD7020] \n
    Rituparno Das [22MSD2027]\n
    ''')


# <=================================== Fetching The Poster For the Movie ===============================================>
def fetch_poster(movie_id):
    url = "https://api.themoviedb.org/3/movie/{}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US".format(movie_id)
    data = requests.get(url,timeout=5)
    data = data.json()
    
    try:
        poster_path = data['poster_path']
        full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
    except KeyError:
        full_path = None
    
    return full_path

# <==================================== Function To Get The Recommended Movie ============================================>
def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_names = []
    recommended_movie_posters = []

    for i in distances[1:user_input+1]:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movie_names.append(movies.iloc[i[0]].title)
        recommended_movie_posters.append(fetch_poster(movie_id))
        

    return recommended_movie_names,recommended_movie_posters

# <----------------------------------for genre based classification ------------------------------>         
def recommend2(movie_df):

    poster_list = []
    movie_titles_list = []
   
    for i in range(no_of_recommendation):

            movie_id = movie_df.iloc[i].movie_id
            poster_list.append(fetch_poster(movie_id))
            movie_titles_list.append(movie_df.iloc[i].title)


    return poster_list,movie_titles_list

# <============================= Loading the Similarity model and the movies data====================>
movies = pickle.load(open('movie_list.pkl','rb'))
similarity = pickle.load(open('similarity.pkl','rb'))



# <============================= Loading the Similarity model and the movies data for genra related classification====================>
movies2  = pickle.load(open('movies_list_based_on_genres.pkl','rb'))
similarity2 = pickle.load(open('cosine_sim_for_genres.pkl','rb'))
genre_list = pickle.load(open('Genre_List.pkl','rb'))

# <==========================Recommendation function based on genres================================>
tfidf = TfidfVectorizer(stop_words='english')
movies2['genres'] = movies2['genres'].fillna('')
tfidf_matrix = tfidf.fit_transform(movies2['genres'])

# <------------------------- Function for getting Recommendation ------------------------------------->
def get_recommendations(genres, data):
    genres_tfidf = tfidf.transform([genres])
    sim_scores = linear_kernel(genres_tfidf, tfidf_matrix).flatten()
    matching_indices = [i for i, score in enumerate(sim_scores) if score > 0]
    sim_scores_indices = sorted(zip(sim_scores[matching_indices], matching_indices), reverse=True)
    
    movie_indices = [index for score, index in sim_scores_indices[:no_of_recommendation]]

    recom =data['title'].iloc[movie_indices].to_frame()
    recom = recom.reset_index().rename(columns={'index':'movie_id'})
    
    return recom



# <------------------ options based on recommendation to get--------------------------------->
option_list = ["Based on movies", "Based on Genres"]

selected_option = st.selectbox(
    "**:blue[Select any option from the dropdown menue ~]**",
    option_list
)

if selected_option == "Based on movies":
        movie_list = movies['title'].values
        selected_movie = st.selectbox(
            "**:blue[Type or select a movie from the dropdown ~]**",
            movie_list
        )
        user_input = int(st.text_input('**:blue[How many movies you want ~]**',3))

        if st.button('Show Recommendation'):
            recommended_movie_names,recommended_movie_posters = recommend(selected_movie)

            for i in range(user_input):
                st.header(recommended_movie_names[i])
                st.image(recommended_movie_posters[i])

else :
     user_input = st.selectbox(
            "**:blue[Type or select a movie genre from the dropdown ~]**",
            genre_list
     )
     no_of_recommendation = int(st.text_input('**:blue[How many movies you want ~]**',3))

     if st.button('Show Recommendation'):
        st.dataframe(get_recommendations(user_input, movies2))

        
        ''' poster_list, movie_titles_list = get_recommendations(user_input,movies2)
        for i in range(no_of_recommendation):
                st.header(movie_titles_list[i])
                st.image(poster_list[i])'''


        
