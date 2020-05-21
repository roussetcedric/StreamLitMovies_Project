import streamlit as st
import pandas as pd
from PIL import Image
import io
import json
import urllib.request
import time

# Load Data -----------------------------------------------------
@st.cache(suppress_st_warning=True)
def load_data():
    df_Movies = pd.read_csv("https://raw.githubusercontent.com/roussetcedric/WCS_Public/master/imdb_movies_light.csv")
    return df_Movies

# Define CSS
st.markdown("""
<style>
body {
  background: url('https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=1950&q=80') center center no-repeat;
  background-size: cover;
  background-attachment: fixed;
  color: white;
  height: 100%;
  width: 100%;
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
 
@st.cache(suppress_st_warning=True)
def DisplayDataFrame(df_Movies,GenreList, DirectorList, ActorList):
    st.write(ActorList)
    df_DisplayLocal = df_Movies[df_Movies["actorsName"].str.contains('|'.join(ActorList))]
    st.write(DirectorList)
    df_DisplayLocal = df_DisplayLocal[df_DisplayLocal["directorsName"].str.contains('|'.join(DirectorList))]
    st.write(GenreList)
    df_DisplayLocal = df_DisplayLocal[df_DisplayLocal["genres"].str.contains('|'.join(GenreList))]
    return df_DisplayLocal

@st.cache(suppress_st_warning=True)
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

@st.cache(suppress_st_warning=True)
def GetNameAndYear(dataFrameParam, movie):
    df_temp = dataFrameParam.loc[dataFrameParam['primaryTitle'].str.lower().str.contains(movie.lower())][['primaryTitle', 'startYear', 'tconst']].sort_values('startYear')
    df_temp['titleYear'] = df_temp['primaryTitle'].map(str) + ' (' + df_temp['startYear'].map(str) + ')'
    df_temp['movieTuple'] = list(zip(df_temp['titleYear'], df_temp['tconst']))
    return df_temp


def main():

    df_Movies = load_data()

    my_bar = st.progress(0)
    for percent_complete in range(100):
        time.sleep(0.01)
        my_bar.progress(percent_complete + 1)

    #Select Movie
    st.title('I Know what you see last night')
    st.write('Tapez un mot clé !')
    title = st.text_input('', '')
    if title != '' :
        df_SelectedNameAndYear = GetNameAndYear(df_Movies, title)
        st.write('Choississez votre film :')
        MovieSelectedTitle = st.selectbox('', df_SelectedNameAndYear["titleYear"].to_list())
        IndiceFilm = df_SelectedNameAndYear[df_SelectedNameAndYear["titleYear"] == MovieSelectedTitle]["tconst"]

        df_MovieSelectedOne = df_Movies[df_Movies["tconst"] == IndiceFilm.iloc[0]]
        DisplayPoster(get_poster_from_api(df_MovieSelectedOne.iloc[0]["tconst"]))
        st.write('Title : ' + str(df_MovieSelectedOne.iloc[0]["originalTitle"]))
        st.write('Year : ' + str(df_MovieSelectedOne.iloc[0]["startYear"]))
        st.write('Duration : ' + str(df_MovieSelectedOne.iloc[0]["runtimeMinutes"]) + 'min')
        st.write('Rating : ' + str(df_MovieSelectedOne.iloc[0]["averageRating"]))

        if st.button('Select This Movie'):
...         MovieIsSelected = True
        else :
            MovieIsSelected = False
        
        # Define Side Menu ----------------------------------------------
        st.sidebar.title("Film Filters")
        ActorList_list = st.sidebar.multiselect("Select Actor", df_MovieSelectedOne.iloc[0]["actorsName"].split(","))
        DirectorList_list = st.sidebar.multiselect("Select Director", df_MovieSelectedOne.iloc[0]["directorsName"].split(","))
        GenreList_list = st.sidebar.multiselect("Select Genre", df_MovieSelectedOne.iloc[0]["genres"].split(","))
    else :
        ActorList_list = ''
        DirectorList_list = ''
        GenreList_list = ''

    df_Display = DisplayDataFrame(df_Movies,GenreList_list, DirectorList_list, ActorList_list)

    if MovieIsSelected :    
        x = st.slider('x', 1, 5)
        if x < df_Display.shape[0]:
            DisplayPoster(get_poster_from_api(df_Display.iloc[x-1]["tconst"]))

if __name__ == '__main__':
    main()