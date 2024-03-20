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
import time
from logutils import get_logger
from constants import (
    WEBDRIVER
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
            filepath = os.path.join('downloads', filename)
            
            # Save the processed image
            image.save(filepath, 'JPEG')
            logger.info(f"Downloaded and processed {filepath}")
    except Exception as e:
        logger.info(f"Could not process {url}. Reason: {e}.")

def collect_image_urls():
    # Setup the driver. This one uses Chrome with the path to your ChromeDriver.
    chrome_options = Options()
    #chrome_options.add_argument("--headless")  
    driver_path = "E:\\PROJECTS\\PAM-2024\\chromedriver.exe"
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    driver.maximize_window()
   # Open the URL
    url = "https://www.google.com/search?q=mukbang%20korean%20girl&tbm=isch&tbs=ic:specific%2Cisc:brown&rlz=1C1CHBF_esDE873DE873&hl=en&sa=X&ved=0CA8Q2J8EahcKEwjA8qDW8YCFAxUAAAAAHQAAAAAQAw&biw=2114&bih=1032"
    driver.get(url)
    
    # Scroll and collect image URLs
    image_urls = set()
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)  # Adjust delay as needed
        
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

def download_images():
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    
    image_urls = collect_image_urls()
    for src in image_urls:
        if not 'google' in src:
            download_and_process_image(src)
        else:
            logger.info(f"Skipping Google-related image: {src}")

if __name__ == "__main__":
    download_images()
