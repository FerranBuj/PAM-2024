import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin
import hashlib
from PIL import Image
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import glob
import gradio as gr
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from logutils import get_logger
from constants import (
    WEBDRIVER
)

from constants import (
    SCRAPER_PATH

)
logger = get_logger("custom_web_scraper")

def image_content_hash(image_content):
    """
    Generates a hash for the given image content using SHA-256.
    """
    return hashlib.sha256(image_content).hexdigest()

def download_and_process_image(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            image_content = response.content
            # Generate a hashcode from the image content
            content_hash = image_content_hash(image_content)
            
            # Open the image directly from the response bytes
            image = Image.open(BytesIO(image_content))
            # Convert image to RGB (in case it's not in that mode, making it compatible with JPG format)
            image = image.convert('RGB')
            
            # Calculate new size respecting the aspect ratio
            if image.width > 480:
                new_height = int((480 / image.width) * image.height)
                image = image.resize((480, new_height), Image.ANTIALIAS)
            
            # Generate a filename based on the content hash
            filename = content_hash + '.jpg'
            filepath = os.path.join(SCRAPER_PATH, filename)
            
            # Save the processed image
            image.save(filepath, 'JPEG')
            logger.info(f"Downloaded and processed {filepath}")
    except Exception as e:
        logger.info(f"Could not process {url}. Reason: {e}.")

def collect_image_urls(URL):
    # Setup the driver. This one uses Chrome with the path to your ChromeDriver.
    chrome_options = Options()
    #chrome_options.add_argument("--headless")  
    driver_path = "E:\\PROJECTS\\PAM-2024\\chromedriver.exe"
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    driver.maximize_window()
   # Open the URL
    driver.get(URL)
    try:
        # Waiting for the div that contains "Aceptar todo" to be clickable
        accept_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'QS5gu') and contains(@class, 'sy4vM') and text()='Aceptar todo']"))
        )
        accept_button.click()
        logger.info("Accepted cookies/terms.")
    except Exception as e:
        logger.warning(f"Could not find or click the acceptance button: {e}")
        
    # Scroll and collect image URLs
    image_urls = set()
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(100)  # Adjust delay as needed
        
        # Find all image elements and extract the src attributes
        images = driver.find_elements(By.TAG_NAME, 'img')
        for image in images:
            src = image.get_attribute('src')
            if src:
                image_urls.add(src)
        
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    
    driver.quit()
    return image_urls

def download_images(URL):
    if not os.path.exists(SCRAPER_PATH):
        os.makedirs(SCRAPER_PATH)

    #TODO Improve scraping
    image_urls = collect_image_urls(URL)
    for src in image_urls:
        if not 'google' in src:
            download_and_process_image(src)
        else:
            logger.info(f"Skipping Google-related image: {src}")
    latest_image = latest_image_for_display()        
    return latest_image, gr.update(value=[latest_image, latest_image])  # Example updat


# Function to find the most recent file in a directory
def latest_file(path):
    list_of_files = glob.glob(path) 
    if not list_of_files:  # if list is empty
        return None
    latest_file = max(list_of_files, key=os.path.getctime)
    return latest_file


def latest_image_for_display():
    """
    Finds the most recent image file, opens it, and returns it in a format
    that can be displayed by Gradio.
    """
    latest_img_path = latest_file(f"{SCRAPER_PATH}/*")
    if latest_img_path:
        # Open and return the image. Note: Gradio can handle PIL Image objects directly.
        with Image.open(latest_img_path) as img:
            return img
    return None  # Return None or a placeholder image if no image is found

# Setting up the Gradio interface
def download_images_wraper(URL):
    download_images(URL)
    return latest_file(URL)

with gr.Blocks() as gradio_interface:
    
    URL = gr.Textbox(label="URL", value="Enter URL", placeholder="Enter URL")
    start_button = gr.Button("Start Scraping")
        
    output_image = gr.Image(label="latest image")
    #examples = gr.Examples(examples=latest_file(f"{SCRAPER_PATH}*"), inputs=start_button, outputs=output_image, fn=lambda x: x)
    
    start_button.click(
        fn=download_images_wraper,
        inputs=URL,
        outputs=output_image
    )           
            

if __name__ == "__main__":
    gradio_interface.launch()