import pickle
import streamlit as st
import requests


# Function to fetch movie poster from TMDB API
def fetch_poster(movie_id):
    """
    Fetches the poster URL for a given movie ID from TMDB API.
    Includes robust error handling for network issues and missing data.
    """
    # Construct the API URL using f-strings for better readability
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"

    try:
        # Make the GET request to the TMDB API with a timeout
        # A timeout prevents the application from hanging indefinitely on network issues
        response = requests.get(url, timeout=10)

        # Raise an HTTPError for bad responses (4xx or 5xx)
        response.raise_for_status()

        # Parse the JSON response
        data = response.json()

        # Safely get 'poster_path' using .get() to avoid KeyError if it's missing
        poster_path = data.get('poster_path')

        # If poster_path exists, construct the full URL
        if poster_path:
            full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
            return full_path
        else:
            # Return a placeholder image if poster_path is missing
            st.warning(f"No poster path found for movie ID: {movie_id}")
            return "https://placehold.co/500x750/cccccc/000000?text=No+Poster"

    except requests.exceptions.Timeout:
        # Handle timeout errors (e.g., network too slow)
        st.error(f"Request timed out for movie ID: {movie_id}. Please try again later.")
        return "https://placehold.co/500x750/ff0000/ffffff?text=Timeout+Error"
    except requests.exceptions.ConnectionError as e:
        # Handle connection errors (e.g., no internet, remote host closed connection)
        st.error(f"Connection error for movie ID: {movie_id}: {e}. Check your internet connection or API status.")
        return "https://placehold.co/500x750/ff0000/ffffff?text=Connection+Error"
    except requests.exceptions.RequestException as e:
        # Handle other request-related exceptions (e.g., HTTP errors, invalid URL)
        st.error(f"Error fetching poster for movie ID: {movie_id}: {e}")
        return "https://placehold.co/500x750/ff0000/ffffff?text=API+Error"
    except Exception as e:
        # Catch any other unexpected errors
        st.error(f"An unexpected error occurred for movie ID: {movie_id}: {e}")
        return "https://placehold.co/500x750/ff0000/ffffff?text=Unknown+Error"


# Recommendation function
def recommend(movie):
    """
    Recommends 5 movies based on the input movie using pre-loaded similarity data.
    Fetches poster for each recommended movie.
    """
    # Safely find the index of the selected movie
    # Check if the movie exists to avoid IndexError
    if movie not in movies['title'].values:
        st.error(f"Sorry, the movie '{movie}' was not found in our database.")
        return [], []  # Return empty lists if movie is not found

    index = movies[movies['title'] == movie].index[0]

    # Get similarity distances for the selected movie
    # Enumerate adds a counter to an iterable, so `x` becomes (index, similarity_score)
    # Sort in reverse (descending) order by the similarity score (x[1])
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])

    recommended_movie_names = []
    recommended_movie_posters = []

    # Loop through the top 5 most similar movies (excluding itself at index 0)
    for i in distances[1:6]:  # Start from index 1 to skip the movie itself
        # Get the movie ID from the 'movies' DataFrame using the index (i[0])
        movie_id = movies.iloc[i[0]].movie_id

        # Fetch the poster for the recommended movie
        recommended_movie_posters.append(fetch_poster(movie_id))

        # Get the title of the recommended movie
        recommended_movie_names.append(movies.iloc[i[0]].title)

    return recommended_movie_names, recommended_movie_posters


# --- Streamlit UI Components ---

st.set_page_config(layout="wide")  # Use wide layout for better display of columns
st.header('Movie Recommender System 🎬')

# Load pre-trained models (movie list and similarity matrix)
# Ensure 'model/' directory exists in the same location as app.py
try:
    movies = pickle.load(open('model/movie_list.pkl', 'rb'))
    similarity = pickle.load(open('model/similarity.pkl', 'rb'))
except FileNotFoundError:
    st.error(
        "Error: Model files not found. Please ensure 'movie_list.pkl' and 'similarity.pkl' are in the 'model/' directory.")
    st.stop()  # Stop the app if models can't be loaded

movie_list = movies['title'].values  # Extract movie titles for the selectbox

# Create a selectbox for the user to choose a movie
selected_movie = st.selectbox(
    "Type or select a movie from the dropdown 👇",
    movie_list
)

# Button to trigger recommendations
if st.button('Show Recommendation ✨'):
    # Call the recommend function
    recommended_movie_names, recommended_movie_posters = recommend(selected_movie)

    # Display recommended movies in columns
    # st.columns is preferred over st.beta_columns as beta_columns is deprecated
    cols = st.columns(5)  # Create 5 columns for 5 recommendations

    for i in range(len(recommended_movie_names)):
        with cols[i]:
            st.text(recommended_movie_names[i])
            st.image(recommended_movie_posters[i])

