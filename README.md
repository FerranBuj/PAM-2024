<h1 style="text-align: center;">Retrieval-Augmented Rasterization</h1>

![image info](./3840_2560_53_80_10_10_oar_True_frame_count_4.png)

# Special Requirements
Python 3.10.4

**Web-Scrapper:**

chromadriver: *https://googlechromelabs.github.io/chrome-for-testing/*

**Rasterizer:**

Java 17 with Windows environment variables properly set. 

# Instructions:

**Web Scrapper**

1. Switch to the 'features/web-scraper' branch if you haven't installed Java 17 yet. 
2. Follow the chromadriver link, download a compatible version and place the 'chromadrive.exe'in the project's main folder.
3. pip install -r 'requirements.txt'
4. Run the main.py script and open the Gradio interface link
5. Run and paste a comma-separated list of urls you wish to scrap. The program will perform several attempts on each url.

Warning:
There's plenty of room for improvement. 
The script often crashes due to the dynamic nature of some of the url stored in the temporary database generated during the scraping, (or at least that's my guess, and Chat GPT's too)

Interaction with acceptance and scrolling buttons could be automated. 

**Retrieval Augmented Rasterization**

The input files folder should have images covering the entire color spectrum of the file to process (circa 10000 small-sized images will do)

1. pip install -r "requirements.txt"
2. Set the resolution, grid, and subgrid values in the config.json file
3. Add the image files to the data/input folder
4. Add frames to process in the data/frames folder
5. Run with "python main.py"

<h3> How it works:</h3>

Each frame is tiled into a grid of x * y tiles and each input image is resized to the size of the frame tiles. The program computes a vector representing the average colors on each tile, subdivided into a second grid, and stores it in an embedding database. The resulting image is formed by querying the vectors of the former frame tiles with those from the available images, choosing the file with a smaller Euclidean distance while ensuring no image is repeated.
