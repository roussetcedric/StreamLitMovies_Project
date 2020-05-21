import streamlit as st
import pandas as pd
from PIL import Image
import io
import json
import urllib.request
import time
import SessionState
from sklearn.neighbors import KNeighborsClassifier

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
def DisplayDataFrame(df_Movies,GenreList, DirectorList, ActorList, WriterList, ComposerList):
    df_DisplayLocal = df_Movies[df_Movies["actorsName"].str.contains('|'.join(ActorList))]
    df_DisplayLocal = df_DisplayLocal[df_DisplayLocal["directorsName"].str.contains('|'.join(DirectorList))]
    df_DisplayLocal = df_DisplayLocal[df_DisplayLocal["genres"].str.contains('|'.join(GenreList))]
    df_DisplayLocal = df_DisplayLocal[df_DisplayLocal["writersName"].str.contains('|'.join(WriterList))]
    df_DisplayLocal = df_DisplayLocal[df_DisplayLocal["composersName"].str.contains('|'.join(ComposerList))]
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

@st.cache(suppress_st_warning=True)
def KnnPrediction(df_Movies,movie_id):
    from sklearn.neighbors import KNeighborsClassifier

    cluster=list(df_Movies['cluster'].loc[df_Movies['tconst']==movie_id])[0]

    df_inter=df_Movies.loc[df_Movies['cluster']==cluster]

    columns=['isAdult','startYear','runtimeMinutes','averageRating','numVotes']

    X=df_inter[columns]
    y=df_inter['tconst']

    caracteristics=[]
    for i in columns:
        caracteristic=list(df_inter[df_inter['tconst']==movie_id][i])[0]
        caracteristics.append(caracteristic)


    model_KNN = KNeighborsClassifier(n_neighbors=5)
    model_KNN.fit(X,y)

    MovieTemp = model_KNN.kneighbors(df_inter.loc[df_inter['tconst']==movieID, columns],n_neighbors=6)
    return MovieTemp[1:6]

def main():

    df_Movies = load_data()
    session_state = SessionState.get(name="", button_selected=False)

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
        st.write('* **Title** : ' + str(df_MovieSelectedOne.iloc[0]["originalTitle"]))
        st.write('* **Year** : ' + str(df_MovieSelectedOne.iloc[0]["startYear"]))
        st.write('* **Duration** : ' + str(df_MovieSelectedOne.iloc[0]["runtimeMinutes"]) + ' min')
        st.write('* **Rating** : ' + str(df_MovieSelectedOne.iloc[0]["averageRating"]))
        st.write('* **Genre** : ' + str(df_MovieSelectedOne.iloc[0]["genres"]))
        st.write('* **Actors** : ' + str(df_MovieSelectedOne.iloc[0]["actorsName"]))
        st.write('* **Directors** : ' + str(df_MovieSelectedOne.iloc[0]["directorsName"]))
        st.write('* **Writers** : ' + str(df_MovieSelectedOne.iloc[0]["writersName"]))
        st.write('* **Composers** : ' + str(df_MovieSelectedOne.iloc[0]["composersName"]))

        
        # Define Side Menu ----------------------------------------------
        st.sidebar.title("Film Filters")
        GenreList_list = st.sidebar.multiselect("Select Genre", df_MovieSelectedOne.iloc[0]["genres"].split(","))
        ActorList_list = st.sidebar.multiselect("Select Actor", df_MovieSelectedOne.iloc[0]["actorsName"].split(","))
        DirectorList_list = st.sidebar.multiselect("Select Director", df_MovieSelectedOne.iloc[0]["directorsName"].split(","))
        WriterList_list = st.sidebar.multiselect("Select Writer", df_MovieSelectedOne.iloc[0]["writersName"].split(","))
        ComposerList_list = st.sidebar.multiselect("Select Composer", df_MovieSelectedOne.iloc[0]["composersName"].split(","))

        if st.button('Select this movie !') :
            session_state.button_selected = True

    else :
        ActorList_list = ''
        DirectorList_list = ''
        GenreList_list = ''
        WriterList_list = ''
        ComposerList_list = ''

    if session_state.button_selected:
        #df_Display = DisplayDataFrame(df_Movies,GenreList_list, DirectorList_list, ActorList_list, WriterList_list, ComposerList_list)
        df_Display = KnnPrediction(df_Movies,IndiceFilm)
        st.dataframe(df_Display)
        x = st.slider('x', 1, 5)
        if x < df_Display.shape[0]:
            DisplayPoster(get_poster_from_api(df_Display.iloc[x-1]["tconst"]))
            st.write('* **Title** : ' + str(df_Display.iloc[x-1]["originalTitle"]))
            st.write('* **Year** : ' + str(df_Display.iloc[x-1]["startYear"]))
            st.write('* **Duration** : ' + str(df_Display.iloc[x-1]["runtimeMinutes"]) + ' min')
            st.write('* **Rating** : ' + str(df_Display.iloc[x-1]["averageRating"]))
            st.write('* **Actors** : ' + str(df_Display.iloc[x-1]["actorsName"]))
            st.write('* **Directors** : ' + str(df_Display.iloc[x-1]["directorsName"]))
            st.write('* **Writers** : ' + str(df_Display.iloc[x-1]["writersName"]))
            st.write('* **Composers** : ' + str(df_Display.iloc[x-1]["composersName"]))

        if st.button('Reset selection !'):
            session_state.button_selected = False
            title = ''

if __name__ == '__main__':
    main()