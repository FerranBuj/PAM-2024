import requests
from PIL import Image
from io import BytesIO
import sqlite3
import os

# Setup your Google API key and Search Engine ID
API_KEY = 'AIzaSyBJf9XS8jxBspkXHo8L0DltQfippCld2wg'
SEARCH_ENGINE_ID = 'd1d56bb262f8941d9'

def create_db_connection():
    """Establish a database connection and return the connection and cursor."""
    conn = sqlite3.connect('images.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS image_data (id INTEGER PRIMARY KEY AUTOINCREMENT, image_url TEXT, file_path TEXT)''')
    return conn, c

def download_image(url):
    """Download an image from a URL and save it to the filesystem."""
    try:
        response = requests.get(url)
        # Check if the response was successful (HTTP status code 200)
        if response.status_code == 200:
            img = Image.open(BytesIO(response.content))
            if not os.path.exists('images'):
                os.makedirs('images')
            file_path = f'images/{url.split("/")[-1].split("?")[0]}'  # Remove query parameters from filename if any
            img.save(file_path)
            return file_path
        else:
            print(f"Failed to download {url} - HTTP status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error downloading or saving image from {url}: {e}")
        return None

def search_and_store_images(query, conn, c, total_images=50):
    """Search for images using Google Custom Search API and store them in the database."""
    num_results_per_query = 10  # Max number of results per query (check API limits)
    num_queries = total_images // num_results_per_query

    for i in range(num_queries):
        start_index = i * num_results_per_query + 1  # Calculate the start index for the current query
        search_url = f"https://www.googleapis.com/customsearch/v1?q={query}&searchType=image&num={num_results_per_query}&start={start_index}&key={API_KEY}&cx={SEARCH_ENGINE_ID}"
        response = requests.get(search_url)
        results = response.json().get('items', [])

        for result in results:
            image_url = result['link']
            file_path = download_image(image_url)
            if file_path:  # Only insert into the database if the image was successfully downloaded and saved
                c.execute("INSERT INTO image_data (image_url, file_path) VALUES (?, ?)", (image_url, file_path))
                conn.commit()

# Establish database connection
conn, c = create_db_connection()
if __name__ == "__main__":
    search_and_store_images('muk bang', conn, c)
    conn.close()