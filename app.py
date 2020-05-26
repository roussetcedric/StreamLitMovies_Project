import streamlit as st
import pandas as pd
from PIL import Image
import io
import json
import urllib.request
import time
import SessionState
from sklearn.neighbors import KNeighborsClassifier
import random
import jellyfish

# Load Data -----------------------------------------------------
@st.cache(suppress_st_warning=True)
def load_data():
    #df_Movies = pd.read_csv("https://raw.githubusercontent.com/roussetcedric/WCS_Public/master/imdb_movies_light.csv")
    df_Movies = pd.read_csv("https://drive.google.com/uc?id=1o7-dyBewlOKIgb9dT9ckXsjvKVZBuduM")
    return df_Movies

@st.cache(suppress_st_warning=True)
def load_data_User():
    df_Users = pd.read_csv("https://drive.google.com/uc?id=1-3xSEOULQXOmMd2Cn-rgQ6JPsitSCz63")
    return df_Users

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
    df_DisplayLocal = df_Movies.fillna(value="")
    df_DisplayLocal = df_DisplayLocal[df_DisplayLocal["actorsName"].str.contains('|'.join(ActorList))]
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
def get_overview_from_api(movie_id):
    MOVIEDB_API_KEY = '076f7a313a578e7764aa7344b143bc30'
    overview = ""
    movie_url = 'https://api.themoviedb.org/3/find/'+movie_id+'?api_key='+MOVIEDB_API_KEY+'&language=fr-FR&external_source=imdb_id'
    try:
        with urllib.request.urlopen(movie_url) as response:
            data = json.loads(response.read())
        overview = data['movie_results'][0]['overview']
    except:
        overview = ""
    return overview

@st.cache(suppress_st_warning=True)
def get_preview_from_api(movie_id):
    MOVIEDB_API_KEY = '076f7a313a578e7764aa7344b143bc30'
    video_url = ''
    movie_url = 'https://api.themoviedb.org/3/movie/'+movie_id+'/videos?api_key='+MOVIEDB_API_KEY+'&language=fr-FR'
    try:
        with urllib.request.urlopen(movie_url) as response:
            data = json.loads(response.read())
        site = data['results'][0]['site']
        if site == 'YouTube':
            video_url = 'https://www.youtube.com/watch?v='+data['results'][0]['key']
        else :
            video_url = ''
    except:
        video_url = ''
    return video_url

@st.cache(suppress_st_warning=True)
def get_actor_pic_from_api(movie_id):
    picList = []
    captionList = []
    MOVIEDB_API_KEY = '076f7a313a578e7764aa7344b143bc30'
    movie_url = 'https://api.themoviedb.org/3/movie/'+movie_id+'/credits?api_key='+MOVIEDB_API_KEY
    try:
        with urllib.request.urlopen(movie_url) as response:
            data = json.loads(response.read())
        cast = data['cast']
        for actor in cast[0:5] :
            picList.append(str("https://image.tmdb.org/t/p/w138_and_h175_face/"+actor["profile_path"]))
            captionList.append(actor["name"] +" - "+ actor["character"])
    except:
        st.write("")
    if(picList) != [] :
        st.image(picList, width=100, caption=captionList)

    return "get_actor_pic_from_api"

@st.cache(suppress_st_warning=True)
def get_director_pic_from_api(movie_id):
    picList = []
    captionList = []
    MOVIEDB_API_KEY = '076f7a313a578e7764aa7344b143bc30'
    movie_url = 'https://api.themoviedb.org/3/movie/'+movie_id+'/credits?api_key='+MOVIEDB_API_KEY
    try:
        with urllib.request.urlopen(movie_url) as response:
            data = json.loads(response.read())
        crew = data['crew']
        for director in crew:
            st.write(director["job"])
            if director["job"] == "Director" :
                picList.append(str("https://image.tmdb.org/t/p/w600_and_h900_bestv2/"+director["profile_path"]))
                captionList.append(director["name"])
                st.write(str("https://image.tmdb.org/t/p/w600_and_h900_bestv2/"+director["profile_path"]))
            else :
                st.write("No Director")
    except:
        st.write("")
    if(picList) != [] :
        st.image(picList, width=100, caption=captionList)

    return "get_pic_from_api"

@st.cache(suppress_st_warning=True)
def GetNameAndYear(dataFrameParam, movie):
    df_temp = dataFrameParam.loc[dataFrameParam['primaryTitle'].str.lower().str.contains(movie.lower())][['primaryTitle', 'startYear', 'tconst']].sort_values('startYear')
    df_temp['titleYear'] = df_temp['primaryTitle'].map(str) + ' (' + df_temp['startYear'].map(str) + ')'
    df_temp['movieTuple'] = list(zip(df_temp['titleYear'], df_temp['tconst']))
    df_temp['Lenght'] = df_temp['primaryTitle'].str.len()
    df_temp['JellyFish'] = dataFrameParam['primaryTitle'].apply(lambda x : jellyfish.levenshtein_distance(x.lower(), movie.lower()))
    df_temp = df_temp.sort_values(by=['JellyFish'])

    return df_temp

@st.cache(suppress_st_warning=True)
def KnnPrediction(df_Movies,df_movie_id):

    movie_id = df_movie_id.iloc[0]
    cluster = df_Movies[df_Movies["tconst"] == movie_id]["cluster"].iloc[0]

    df_inter=df_Movies.loc[df_Movies['cluster']==cluster]

    if df_inter.shape[0] < 6 :
        df_Cluster = df_Movies
    else : 
        columns=['isAdult','startYear','runtimeMinutes','averageRating','numVotes']

        X=df_inter[columns]
        y=df_inter['tconst']

        model_KNN = KNeighborsClassifier(n_neighbors=5)
        model_KNN.fit(X,y)

        MovieTemp = model_KNN.kneighbors(df_inter.loc[df_inter['tconst']==movie_id, columns],n_neighbors=6)

        clusterList = []
        for i in range(1,6):
            clusterList.append(df_inter.iloc[MovieTemp[1][0][i]]['tconst'])

        df_Cluster = df_Movies[df_Movies["tconst"].isin(clusterList)]
    return df_Cluster

def main():

    df_Movies = load_data()
    df_Users = load_data_User()
    session_state = SessionState.get(name="", button_selected=False)

    my_bar = st.progress(0)
    for percent_complete in range(100):
        time.sleep(0.01)
        my_bar.progress(percent_complete + 1)

    #Select Movie
    st.title('I know what you saw last night')
    st.write('Type your movie title here !')
    title = st.text_input('', '')
    if title != '' :
        df_SelectedNameAndYear = GetNameAndYear(df_Movies, title)
        st.write('Choose ypur movie :')
        MovieSelectedTitle = st.selectbox('', df_SelectedNameAndYear["titleYear"].to_list())
        IndiceFilm = df_SelectedNameAndYear[df_SelectedNameAndYear["titleYear"] == MovieSelectedTitle]["tconst"]

        df_MovieSelectedOne = df_Movies[df_Movies["tconst"] == IndiceFilm.iloc[0]]
        DisplayPoster(get_poster_from_api(df_MovieSelectedOne.iloc[0]["tconst"]))
        st.write('* **Title** : ' + str(df_MovieSelectedOne.iloc[0]["originalTitle"]))
        st.write('* **Résumé** : ' + str(get_overview_from_api(IndiceFilm.iloc[0])))
        st.write('* **Year** : ' + str(df_MovieSelectedOne.iloc[0]["startYear"]))
        st.write('* **Duration** : ' + str(df_MovieSelectedOne.iloc[0]["runtimeMinutes"]) + ' min')
        st.write('* **Rating** : ' + str(df_MovieSelectedOne.iloc[0]["averageRating"]))
        st.write('* **Genre** : ' + str(df_MovieSelectedOne.iloc[0]["genres"]))
        st.write('* **Actors** : ' + str(df_MovieSelectedOne.iloc[0]["actorsName"]))
        get_actor_pic_from_api(df_MovieSelectedOne.iloc[0]["tconst"])
        st.write('* **Directors** : ' + str(df_MovieSelectedOne.iloc[0]["directorsName"]))
        get_director_pic_from_api(df_MovieSelectedOne.iloc[0]["tconst"])
        st.write('* **Writers** : ' + str(df_MovieSelectedOne.iloc[0]["writersName"]))
        if pd.notna(df_MovieSelectedOne.iloc[0]["composersName"]) :
            st.write('* **Composers** : ' + str(df_MovieSelectedOne.iloc[0]["composersName"]))
        preview_url = get_preview_from_api(IndiceFilm.iloc[0])
        if preview_url != '':
            st.write('* **Preview** : ' + str(preview_url))

        # Define Side Menu ----------------------------------------------
        st.sidebar.title("Film Filters")
        GenreList_list = st.sidebar.multiselect("Select Genre", df_MovieSelectedOne.iloc[0]["genres"].split(","))
        ActorList_list = st.sidebar.multiselect("Select Actor", df_MovieSelectedOne.iloc[0]["actorsName"].split(","))
        DirectorList_list = st.sidebar.multiselect("Select Director", df_MovieSelectedOne.iloc[0]["directorsName"].split(","))
        WriterList_list = st.sidebar.multiselect("Select Writer", df_MovieSelectedOne.iloc[0]["writersName"].split(","))
        if pd.notna(df_MovieSelectedOne.iloc[0]["composersName"]) :
            ComposerList_list = st.sidebar.multiselect("Select Composer", df_MovieSelectedOne.iloc[0]["composersName"].split(","))
        else : 
            ComposerList_list = []

        if st.button('Select this movie !') :
            session_state.button_selected = True

    else :
        ActorList_list = []
        DirectorList_list = []
        GenreList_list = []
        WriterList_list = []
        ComposerList_list = []

    if session_state.button_selected:
        Model = st.sidebar.radio("Prediction Model",["Movie_Recommandation","User_Recommandantion"])
        st.write(Model)

        df_Filtered = DisplayDataFrame(df_Movies,GenreList_list, DirectorList_list, ActorList_list, WriterList_list, ComposerList_list)
        if Model == "Movie_Recommandation" :
            st.write("Movie_Recommandation")
            df_Display = KnnPrediction(df_Filtered,IndiceFilm)
        elif Model == "User_Recommandantion"
            st.write("User_Recommandantion")
            df_Display = df_Filtered

        x = st.slider('x', 1, df_Display.shape[0])
        if x <= df_Display.shape[0]:
            DisplayPoster(get_poster_from_api(df_Display.iloc[x-1]["tconst"]))
            score = random.randint(1, 100)
            st.write('* **Recommandation** : ' + str(score) + '%')
            my_bar = st.progress(score)
            if pd.notna(df_Display.iloc[x-1]["originalTitle"]) :
                st.write('* **Title** : ' + str(df_Display.iloc[x-1]["originalTitle"]))
            st.write('* **Résumé** : ' + str(get_overview_from_api(df_Display.iloc[x-1]["tconst"])))
            if pd.notna(df_Display.iloc[x-1]["startYear"]) :
                st.write('* **Year** : ' + str(df_Display.iloc[x-1]["startYear"]))
            if pd.notna(df_Display.iloc[x-1]["runtimeMinutes"]) :
                st.write('* **Duration** : ' + str(df_Display.iloc[x-1]["runtimeMinutes"]) + ' min')
            if pd.notna(df_Display.iloc[x-1]["averageRating"]) :
                st.write('* **Rating** : ' + str(df_Display.iloc[x-1]["averageRating"]))
            if pd.notna(df_Display.iloc[x-1]["actorsName"]) :
                st.write('* **Actors** : ' + str(df_Display.iloc[x-1]["actorsName"]))
            get_actor_pic_from_api(df_Display.iloc[x-1]["tconst"])
            if pd.notna(df_Display.iloc[x-1]["directorsName"]) :
                st.write('* **Directors** : ' + str(df_Display.iloc[x-1]["directorsName"]))
            if pd.notna(df_Display.iloc[x-1]["writersName"]) :
                st.write('* **Writers** : ' + str(df_Display.iloc[x-1]["writersName"]))
            if pd.notna(df_Display.iloc[x-1]["composersName"]) :
                st.write('* **Composers** : ' + str(df_Display.iloc[x-1]["composersName"]))
            preview_url = get_preview_from_api(df_Display.iloc[x-1]["tconst"])
            if preview_url != '':
                st.write('* **Preview** : ' + str(preview_url))

if __name__ == '__main__':
    main()