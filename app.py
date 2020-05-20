import streamlit as st
import pandas as pd
from PIL import Image
import io
import json
import urllib.request
import time

# Load Data -----------------------------------------------------
df_Movies = pd.read_csv("https://raw.githubusercontent.com/roussetcedric/WCS_Public/master/imdb_movies_light.csv")

# Define CSS
st.markdown("""
<style>
body {
    color: #fff;
    background-color: #111;
    etc. 
}
</style>
    """, unsafe_allow_html=True)

# Define Function --------------------------------------------


def DisplayPoster(UrlToDisplay):
    if UrlToDisplay:
        with urllib.request.urlopen(UrlToDisplay) as url:
            f = io.BytesIO(url.read())
        img = Image.open(f)
        st.image(img, width=400)
 

def DisplayDataFrame(GenreList, DirectorList, ActorList):
    st.write(ActorList)
    df_DisplayLocal = df_Movies[df_Movies["actorsName"].str.contains('|'.join(ActorList))]
    st.write(DirectorList)
    df_DisplayLocal = df_DisplayLocal[df_DisplayLocal["directorsName"].str.contains('|'.join(DirectorList))]
    st.write(GenreList)
    df_DisplayLocal = df_DisplayLocal[df_DisplayLocal["genres"].str.contains('|'.join(GenreList))]
    return df_DisplayLocal


def get_poster_from_api(movie_id):
    MOVIEDB_API_KEY = '076f7a313a578e7764aa7344b143bc30'
    poster_base_url = 'https://image.tmdb.org/t/p/original'
    poster_url = ''
    movie_url = 'https://api.themoviedb.org/3/find/'+movie_id+'?api_key='+MOVIEDB_API_KEY+'&language=fr-FR&external_source=imdb_id'
    try:
        with urllib.request.urlopen(movie_url) as response:
            data = json.loads(response.read())
        poster_url = poster_base_url+data['movie_results'][0]['poster_path']
    except:
        poster_url = "https://raw.githubusercontent.com/roussetcedric/WCS_Public/master/pngtree-latest-movie-poster-design-image_163485.jpg"
    return poster_url


def GetNameAndYear(dataFrameParam, movie):
    df_temp = dataFrameParam.loc[dataFrameParam['primaryTitle'].str.lower().str.contains(movie.lower())][['primaryTitle', 'startYear', 'tconst']].sort_values('startYear')
    df_temp['titleYear'] = df_temp['primaryTitle'].map(str) + ' (' + df_temp['startYear'].map(str) + ')'
    df_temp['movieTuple'] = list(zip(df_temp['titleYear'], df_temp['tconst']))
    return df_temp


def main():
    my_bar = st.progress(0)
    for percent_complete in range(100):
        time.sleep(0.01)
        my_bar.progress(percent_complete + 1)

    #Select Movie
    title = st.text_input('Cherchez votre film', 'Taper un mot clé ici !')
    df_SelectedNameAndYear = GetNameAndYear(df_Movies, title)
    MovieSelectedTitle = st.selectbox('Choississez votre film ?', df_SelectedNameAndYear["titleYear"].to_list())
    IndiceFilm = df_SelectedNameAndYear[df_SelectedNameAndYear["titleYear"] == MovieSelectedTitle]["tconst"]
    st.write(IndiceFilm)
    df_MovieSelectedOne = df_Movies[df_Movies["tconst"] == IndiceFilm.iloc[0]]
    st.dataframe(df_MovieSelectedOne)
    DisplayPoster(get_poster_from_api(df_MovieSelectedOne.iloc[0]["tconst"]))
    # Define Side Menu ----------------------------------------------
    st.sidebar.title("Film Filters")
    ActorList_list = st.sidebar.multiselect("Select Actor", df_MovieSelectedOne.iloc[0]["actorsName"].split(","))
    DirectorList_list = st.sidebar.multiselect("Select Director", df_MovieSelectedOne.iloc[0]["directorsName"].split(","))
    GenreList_list = st.sidebar.multiselect("Select Genre", df_MovieSelectedOne.iloc[0]["genres"].split(","))

    df_Display = DisplayDataFrame(GenreList_list, DirectorList_list, ActorList_list)
    
    x = st.slider('x', 1, 5)
    DisplayPoster(get_poster_from_api(df_Display.iloc[x-1]["tconst"]))

if __name__ == '__main__':
    main()