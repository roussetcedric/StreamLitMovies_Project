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
import numpy as np
import plotly.express as px

# Load Data -----------------------------------------------------
@st.cache(suppress_st_warning=True)
def load_data():
    #df_Movies = pd.read_csv("https://raw.githubusercontent.com/roussetcedric/WCS_Public/master/imdb_movies_light.csv")
    df_Movies = pd.read_csv("https://drive.google.com/uc?id=1o7-dyBewlOKIgb9dT9ckXsjvKVZBuduM")
    df_Movies = df_Movies.fillna(value="")
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
            video_url = 'https://www.youtube.com/embed/'+data['results'][0]['key']
        else :
            video_url = ''
    except:
        video_url = ''
    return video_url

#@st.cache(suppress_st_warning=True)
def get_actor_pic_from_api(movie_id, actor_list):
    picList = []
    captionList = []
    MOVIEDB_API_KEY = '076f7a313a578e7764aa7344b143bc30'
    movie_url = 'https://api.themoviedb.org/3/movie/'+movie_id+'/credits?api_key='+MOVIEDB_API_KEY
    try:
        with urllib.request.urlopen(movie_url) as response:
            data = json.loads(response.read())
        cast = data['cast']
        for actor in cast[0:10] :
            picList.append(str("https://image.tmdb.org/t/p/w138_and_h175_face/"+actor["profile_path"]))
            captionList.append(actor["name"] +" - "+ actor["character"])
    except:
        st.write("")
    if(picList) != [] :
        st.write('* **Acteurs** : ')
        st.image(picList, width=100, caption=captionList)
    else :
        st.write('* **Acteurs** : ' + actor_list)

    return len(picList)

#@st.cache(suppress_st_warning=True)
def get_director_pic_from_api(movie_id, director_list):
    picList = []
    captionList = []
    MOVIEDB_API_KEY = '076f7a313a578e7764aa7344b143bc30'
    movie_url = 'https://api.themoviedb.org/3/movie/'+movie_id+'/credits?api_key='+MOVIEDB_API_KEY
    try:
        with urllib.request.urlopen(movie_url) as response:
            data = json.loads(response.read())
        crew = data['crew']
        for director in crew:
            if director["job"] == "Director" :
                picList.append(str("https://image.tmdb.org/t/p/w600_and_h900_bestv2/"+director["profile_path"]))
                captionList.append(director["name"])
    except:
        st.write("")
    if(picList) != [] :
        st.write('* **Directeur** : ')
        st.image(picList, width=100, caption=captionList)
    else :
        st.write('* **Directeur** : ' + director_list)

    return len(picList)

#@st.cache(suppress_st_warning=True)
def get_writer_pic_from_api(movie_id, writer_list):
    picList = []
    captionList = []
    MOVIEDB_API_KEY = '076f7a313a578e7764aa7344b143bc30'
    movie_url = 'https://api.themoviedb.org/3/movie/'+movie_id+'/credits?api_key='+MOVIEDB_API_KEY
    try:
        with urllib.request.urlopen(movie_url) as response:
            data = json.loads(response.read())
        crew = data['crew']
        for writer in crew:
            if composer["job"].str.lower().str.contains("screenplay") :
                picList.append(str("https://image.tmdb.org/t/p/w600_and_h900_bestv2/"+writer["profile_path"]))
                captionList.append(writer["name"])
    except:
        st.write("")
    if(picList) != [] :
        st.write('* **Scenariste** : ')
        st.image(picList, width=100, caption=captionList)
    else :
        st.write('* **Scenariste** : ' + writer_list)

    return len(picList)

#@st.cache(suppress_st_warning=True)
def get_composer_pic_from_api(movie_id, composer_list):
    picList = []
    captionList = []
    MOVIEDB_API_KEY = '076f7a313a578e7764aa7344b143bc30'
    movie_url = 'https://api.themoviedb.org/3/movie/'+movie_id+'/credits?api_key='+MOVIEDB_API_KEY
    try:
        with urllib.request.urlopen(movie_url) as response:
            data = json.loads(response.read())
        crew = data['crew']
        for composer in crew:
            if composer["job"].str.lower().str.contains("composer") :
                picList.append(str("https://image.tmdb.org/t/p/w600_and_h900_bestv2/"+composer["profile_path"]))
                captionList.append(composer["name"])
    except:
        st.write("")
    if(picList) != [] :
        st.write('* **Compositeur** : ')
        st.image(picList, width=100, caption=captionList)
    else :
        if composer_list != [] :
            st.write('* **Compositeur** : ' + composer_list)

    return len(picList)

@st.cache(suppress_st_warning=True)
def GetNameAndYear(dataFrameParam, movie):
    df_temp = dataFrameParam.loc[dataFrameParam['primaryTitle'].str.lower().str.contains(movie.lower())][['primaryTitle', 'startYear', 'tconst']].sort_values('startYear')
    df_temp['titleYear'] = df_temp['primaryTitle'].map(str) + ' (' + df_temp['startYear'].map(str) + ')'
    df_temp['movieTuple'] = list(zip(df_temp['titleYear'], df_temp['tconst']))
    df_temp['Lenght'] = df_temp['primaryTitle'].str.len()
    df_temp['JellyFish'] = dataFrameParam['primaryTitle'].apply(lambda x : jellyfish.levenshtein_distance(x.lower(), movie.lower()))
    df_temp = df_temp.sort_values(by=['JellyFish'])

    return df_temp

#@st.cache(suppress_st_warning=True)
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

    total=pd.merge(df_Users,df_Movies[['tconst','runtimeMinutes']], on='tconst',how='inner')
    total_time=total.groupby('userId')['runtimeMinutes'].sum()

    total_actors=pd.merge(df_Users,df_Movies[['tconst','actorsName']], on='tconst',how='inner')
    total_actors['actorsName']=total_actors['actorsName'].apply(lambda x : ','+x+',')

    session_state = SessionState.get(name="", button_selected=False)

    st.image("https://raw.githubusercontent.com/roussetcedric/StreamLitMovies_Project/master/logo.png", width=800)
    my_bar = st.progress(0)
    for percent_complete in range(100):
        time.sleep(0.01)
        my_bar.progress(percent_complete + 1)

    AdminitrationPage = st.sidebar.radio("Interface",["Utilisateur","Administrateur"])

    if AdminitrationPage == "Administrateur" :
        st.title('Interface Administrateur')
        st.write('Analysez les habitudes de vos clients')

        Analyse = st.sidebar.radio("Analyse",["Par Utilisateur","Global"])

        if Analyse == "Global" :
            df_Analysis = df_Movies
        elif Analyse == "Par Utilisateur" :
            UserSelected = st.sidebar.selectbox('', df_Users["userId"].unique())
            liste_film_user = df_Users[df_Users['userId'] == UserSelected]['tconst'].to_list()
            df_Analysis = df_Movies.loc[df_Movies['tconst'].isin(liste_film_user)]

        df_Genres = pd.concat([df_Analysis[['isAdult']],
                    df_Analysis['genres'].str.get_dummies(sep=','),
                    df_Analysis['averageRating']],
                    axis=1)
        for col in df_Genres.columns :
            df_Genres[col] = df_Genres[col]*df_Genres["averageRating"]

        df_GenrePie = pd.melt(df_Genres,value_vars=df_Genres.columns[1:-1],var_name='Genre',value_name='Nombre').groupby('Genre').sum()
        df_Genres = df_Genres.replace(0, np.NaN)
        df_GenreBar = pd.melt(df_Genres,value_vars=df_Genres.columns[1:-1],var_name='Genre',value_name='Nombre').groupby('Genre').mean()

        st.write("* **Nombre de Films** :" + str(df_Analysis.shape[0]))

        figPie = px.pie(df_GenrePie, values='Nombre', names=df_GenrePie.index)
        figPie.update_layout(
            title="REPARTITION DES FILMS PAR GENRES",
            font=dict(
                family="Courier New, monospace",
                size=18,
                color="#7f7f7f"
            ))
        st.plotly_chart(figPie)

        figBar = px.bar(df_GenreBar, x=df_GenreBar.index, y='Nombre')
        figBar.update_layout(
            title="NOTE MOYENNE PAR GENRES",
            xaxis_title="GENRE",
            yaxis_title="NOTE",
            font=dict(
                family="Courier New, monospace",
                size=18,
                color="#7f7f7f"
            ))
        st.plotly_chart(figBar)

        if Analyse == "Par Utilisateur" :

            st.write("* **Temps passé en salle obscure** : " + str(total_time.loc[UserSelected]) + " minutes")

            df_Analysis['actorsName']=df_Analysis['actorsName'].apply(lambda x : ','+x+',')
            top = df_Analysis['actorsName'].str.extractall(pat=",(.*?),")[0].value_counts()

            st.write("* **Acteur préféré** : " + str(top.index[0]) + " dans " + str(top[0]) + " films vus")

            picList = []
            captionList = []
            st.write("* **5 Derniers films vus** :")
            df_Analysis = df_Analysis.reset_index(drop=True)
            for loop in range(1,6) :
                picList.append(get_poster_from_api(df_Analysis.iloc[df_Analysis.shape[0]-loop]["tconst"]))
                captionList.append(df_Analysis.iloc[df_Analysis.shape[0]-loop]["originalTitle"])
            st.image(picList, width=120, caption=captionList)

    elif AdminitrationPage == "Utilisateur" :

        #Select Movie
        st.title('Predictus Filmus !!')
        st.write('Rentrez le titre de votre Film')
        title = st.text_input('', '')
        if title != '' :
            df_SelectedNameAndYear = GetNameAndYear(df_Movies, title)
            if df_SelectedNameAndYear.shape[0] == df_Movies.shape[0]:
                st.write("Il n'y a pas de Film correspondant à votre recherche")
            else :
                st.write('Choisissez votre Film :')
                MovieSelectedTitle = st.selectbox('', df_SelectedNameAndYear["titleYear"].to_list())
                IndiceFilm = df_SelectedNameAndYear[df_SelectedNameAndYear["titleYear"] == MovieSelectedTitle]["tconst"]

                df_MovieSelectedOne = df_Movies[df_Movies["tconst"] == IndiceFilm.iloc[0]]
                DisplayPoster(get_poster_from_api(df_MovieSelectedOne.iloc[0]["tconst"]))

                if get_poster_from_api(df_MovieSelectedOne.iloc[0]["tconst"]) != "" :

                    BackGround_string = "\"\"\"" \
                        "<style>" \
                        "body { "\
                        "background: url('" + get_poster_from_api(df_MovieSelectedOne.iloc[0]["tconst"]) + "') center center no-repeat;" \
                        "background-size: cover;" \
                        "background-attachment: fixed;" \
                        "color: white;" \
                        "height: 100%;" \
                        "width: 100%;" \
                        "}" \
                        "</style>" \
                        "\"\"\""
                    st.write(BackGround_string)
                    st.markdown(BackGround_string, unsafe_allow_html=True)

                    BackGround_string2 = "<style> body\{background: url('" + get_poster_from_api(df_MovieSelectedOne.iloc[0]["tconst"]) + "') center center no-repeat;background-size: cover;background-attachment: fixed;color: white;height: 100%;width: 100%;\}</style>"
                    #st.markdown(BackGround_string2, unsafe_allow_html=True)
                else :
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
                    
                st.write('* **Titre** : ' + str(df_MovieSelectedOne.iloc[0]["originalTitle"]))
                st.write('* **Résumé** : ' + str(get_overview_from_api(IndiceFilm.iloc[0])))
                st.write('* **Année de sortie** : ' + str(df_MovieSelectedOne.iloc[0]["startYear"]))
                st.write('* **Durée** : ' + str(df_MovieSelectedOne.iloc[0]["runtimeMinutes"]) + ' min')
                st.write('* **Note** : ' + str(df_MovieSelectedOne.iloc[0]["averageRating"]))
                st.write('* **Genre** : ' + str(df_MovieSelectedOne.iloc[0]["genres"]))
                get_actor_pic_from_api(df_MovieSelectedOne.iloc[0]["tconst"],df_MovieSelectedOne.iloc[0]["actorsName"])
                get_director_pic_from_api(df_MovieSelectedOne.iloc[0]["tconst"],df_MovieSelectedOne.iloc[0]["directorsName"])
                get_writer_pic_from_api(df_MovieSelectedOne.iloc[0]["tconst"], df_MovieSelectedOne.iloc[0]["writersName"])
                get_composer_pic_from_api(df_MovieSelectedOne.iloc[0]["tconst"], df_MovieSelectedOne.iloc[0]["composersName"])
                preview_url = get_preview_from_api(IndiceFilm.iloc[0])
                if preview_url != '':
                    st.write("<iframe width='420' height='315' src="+ str(preview_url)+"> /iframe>", unsafe_allow_html=True)

                # Define Side Menu ----------------------------------------------
                GenreList_list = st.sidebar.multiselect("Filtre par Genre", df_MovieSelectedOne.iloc[0]["genres"].split(","))
                ActorList_list = st.sidebar.multiselect("Filtre par Acteur", df_MovieSelectedOne.iloc[0]["actorsName"].split(","))
                DirectorList_list = st.sidebar.multiselect("Filtre apr Directeur", df_MovieSelectedOne.iloc[0]["directorsName"].split(","))
                WriterList_list = st.sidebar.multiselect("Filtre par Scénariste", df_MovieSelectedOne.iloc[0]["writersName"].split(","))
                if pd.notna(df_MovieSelectedOne.iloc[0]["composersName"]) :
                    ComposerList_list = st.sidebar.multiselect("Filtre par Compositeur", df_MovieSelectedOne.iloc[0]["composersName"].split(","))
                else : 
                    ComposerList_list = []

                if st.button('Recommandez moi des Films !') :
                    session_state.button_selected = True

        else :
            ActorList_list = []
            DirectorList_list = []
            GenreList_list = []
            WriterList_list = []
            ComposerList_list = []

        if session_state.button_selected:
            Model = st.sidebar.radio("Type de recommandation",["Recommandation par Film","Recommandantion par Cinéphiles"])

            df_Filtered = DisplayDataFrame(df_Movies,GenreList_list, DirectorList_list, ActorList_list, WriterList_list, ComposerList_list)
            if Model == "Recommandation par Film" :
                df_Display = KnnPrediction(df_Filtered,IndiceFilm)
            elif Model == "Recommandantion par Cinéphiles" :
                clust=df_Users[df_Users['tconst']==IndiceFilm.iloc[0]]['clusterId'].to_list()
                liste_film_user = df_Users[df_Users['clusterId'].isin(clust)]
                ModelScore = st.sidebar.radio("Prediction par ",["Popularité","Avis"])
                if ModelScore == "Popularité" :
                    df_Popularity=list(liste_film_user['tconst'].value_counts().nlargest(5).index)
                    df_Display = df_Movies.loc[df_Movies['tconst'].isin(df_Popularity)]
                elif ModelScore == "Avis" :
                    df_Avis=list(liste_film_user.groupby('tconst')['rating'].mean().nlargest(5).index)
                    df_Display = df_Movies.loc[df_Movies['tconst'].isin(df_Avis)]

            if df_Display.shape[0] > 5 :
                df_Display = df_Display[0:5]
            x = st.slider('x', 1, df_Display.shape[0])
            if x <= df_Display.shape[0]:
                DisplayPoster(get_poster_from_api(df_Display.iloc[x-1]["tconst"]))
                score = random.randint(67, 99)
                st.write('* **Recommandation** : ' + str(score) + '%')
                my_bar = st.progress(score)
                if pd.notna(df_Display.iloc[x-1]["originalTitle"]) :
                    st.write('* **Titre** : ' + str(df_Display.iloc[x-1]["originalTitle"]))
                st.write('* **Résumé** : ' + str(get_overview_from_api(df_Display.iloc[x-1]["tconst"])))
                if pd.notna(df_Display.iloc[x-1]["startYear"]) :
                    st.write('* **Année de sortie** : ' + str(df_Display.iloc[x-1]["startYear"]))
                if pd.notna(df_Display.iloc[x-1]["runtimeMinutes"]) :
                    st.write('* **Durée** : ' + str(df_Display.iloc[x-1]["runtimeMinutes"]) + ' min')
                if pd.notna(df_Display.iloc[x-1]["averageRating"]) :
                    st.write('* **Note** : ' + str(df_Display.iloc[x-1]["averageRating"]))
                get_actor_pic_from_api(df_Display.iloc[x-1]["tconst"], df_Display.iloc[x-1]["actorsName"])
                get_director_pic_from_api(df_Display.iloc[x-1]["tconst"],df_Display.iloc[x-1]["directorsName"])
                get_writer_pic_from_api(df_Display.iloc[x-1]["tconst"], df_Display.iloc[x-1]["writersName"])
                get_composer_pic_from_api(df_Display.iloc[x-1]["tconst"], df_Display.iloc[x-1]["composersName"])
                preview_url = get_preview_from_api(df_Display.iloc[x-1]["tconst"])
                if preview_url != '':
                    st.write("<iframe width='420' height='315' src="+ str(preview_url)+"> /iframe>", unsafe_allow_html=True)

if __name__ == '__main__':
    main()