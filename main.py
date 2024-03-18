import time
import py5
import os
import glob
from pathlib import Path
from constants import(
        SIZE_W, SIZE_H,
        TILE_X, TILE_Y,
        TILE_W, TILE_H,
        MATRIX_X, MATRIX_Y,
        MATRIX_W, MATRIX_H,
        SKETCH_PATH, FRAMES, FILES,
        COLLECTION_NAME
)

import gradio as gr
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from db_utils import get_chroma_client
from logutils import get_logger
logger = get_logger("main")
#due to the py5 library constraints
#variables initialized in settings and setup must be declared as globals
pg_frame_tiles = []
frame_matrices = []
def settings():
    py5.size(SIZE_W, SIZE_H, py5.P2D) #settings() allows passing variables to py.size() width and height.

def setup():
    global collection, client, render_pg, pg_frame_tiles, frame_matrices

    #py5.create_graphics()
    render_pg = py5.create_graphics(SIZE_W, SIZE_H)
    client = get_chroma_client()
    '''
    try:
        client.delete_collection(name=COLLECTION_NAME) # Delete a collection and all associated embeddings, documents, and metadata. ⚠️ This is destructive and not reversible

    except:
        logger.info("Couldn't delete previous collection. Creating a new one.")
    '''
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hsnw:space":"l2"}        
    )
    
    pg_frame_tiles, frame_matrices = initialize_frame(FRAMES[0], pg_frame_tiles, frame_matrices)
    printer("Frame successfully processed")
    initialize_file(FILES) #Initializes only one frame
    printer("Files successfully processed and stored")

def draw():
    global frame_matrices, pg_frame_tiles
    #debug_setup(pg_frame_tiles)  
    #py5.image_mode(py5.CENTER)
    pg = rasterize(render_pg)
    #py5.image(pg, py5.width/2, py5.height/2)
    frame_name = f"data/output/{TILE_X}_{TILE_Y}_{MATRIX_X}_{MATRIX_Y}_frame_count_{py5.frame_count}.png"
    pg.save(f"{os.path.join(frame_name)}")

    if py5.frame_count < len(FRAMES)-1:
        pg_frame_tiles = []
        frame_matrices = []
        pg_frame_tiles, frame_matrices = initialize_frame(FRAMES[py5.frame_count], pg_frame_tiles, frame_matrices)
    logger.info(f"{py5.frame_count}")

def printer(input):
    logger.info(f"{input}")

def initialize_frame(frame, pg_frame_tiles, frame_matrices):
    frame = py5.load_image(frame)
    resize_pg = py5.create_graphics(SIZE_W, SIZE_H, py5.P2D)
    resize_pg.begin_draw()
    resize_pg.image(frame, 0, 0, SIZE_W, SIZE_H)
    resize_pg.end_draw()
    frame = resize_pg

    for y in range(0, SIZE_H, TILE_H):    
        for x in range(0, SIZE_W, TILE_W):
            tile = frame.get_pixels(int(x), int(y), TILE_W, TILE_H)
            temp_pg = py5.create_graphics(int(TILE_W), int(TILE_H), py5.P2D)
            temp_pg.begin_draw()
            temp_pg.image(tile, 0, 0, int(TILE_W), int(TILE_H))
            temp_pg.end_draw()
            pg_frame_tiles.append(temp_pg)
            frame_matrices = color_matrix(temp_pg, False, None, frame_matrices)
    return pg_frame_tiles, frame_matrices

def initialize_file(files): #pg_files_tiles):
    file_index = 0
    for file in files:
        file = py5.load_image(file)
        temp_pg = py5.create_graphics(TILE_W, TILE_H, py5.P2D)
        temp_pg.begin_draw()
        temp_pg.image(file, 0, 0, TILE_W, TILE_H)
        temp_pg.end_draw()
        #pg_files_tiles.append(temp_pg)
        color_matrix(temp_pg, True, file_index)
        file_index = file_index+1
        #return pg_files_tiles
                    
def color_matrix(pg, store_matrices = False, index = None, matrices = None):
    matrix = [[0 for _ in range(4)] for _ in range(MATRIX_X * MATRIX_Y)]
    inner_index = 0
    for y in range(0, TILE_H, MATRIX_H):    
        for x in range(0, TILE_W, MATRIX_W):
            sum_a = sum_r = sum_g = sum_b = 0
            pg_matrix = pg.get_pixels(x, y, MATRIX_W, MATRIX_H)
            color_count = 0
            for pixel_y in range(MATRIX_H):
                for pixel_x in range(MATRIX_W):
                    c = pg_matrix.get_pixels(pixel_x, pixel_y)
                    
                    a = (c >> 24) & 0xFF #Check!
                    r = (c >> 16) & 0xFF
                    g = (c >> 8) & 0xFF
                    b = c & 0xFF

                    sum_a += a
                    sum_r += r
                    sum_g += g
                    sum_b += b
                    color_count += 1
            if color_count > 0:
                matrix[inner_index] = [
                    sum_r // color_count,
                    sum_g // color_count,
                    sum_b // color_count,
                    sum_a // color_count,
                ]
            #logger.info(f"subtile: {sub_tiles_index}, x: {x}, y: {y}, main color: {matrix[sub_tiles_index]}")
            if inner_index < (MATRIX_X * MATRIX_Y) - 1:
                inner_index += 1            
    if store_matrices:
        store_matrix(index, matrix)
    else:
        matrices.append(matrix)        
        return matrices
    
def euclidean_distance(frame_matrix): #for each frame tile, get the closest file tile.
    index = 0
    vector = []
    for rgba in frame_matrix: #matrix_x * matrix_y length
        vector.append(((rgba[0]<< 24) + (rgba[1] << 16) + (rgba[2] << 8) + (rgba[3])))         
    results = collection.query(
        query_embeddings=[vector],
        n_results=1,
        include=["distances"] #ids are always returned
    )

    '''
    j= subtile_index
    frame tile        file image tile[]   
        ___________       ___________                     ____         ____
    |j0|__|__|__| --> |j0|__|__|__|  --> distance += j0-n|rgba| - j0-n|rgba| 
    |__|__|__|__|     |__|__|__|__|        
    |__|__|__|__|     |__|__|__|__|
    |__|__|__|jn|     |__|__|__|jn|
    '''    
    #logger.info(f"query color={results['ids']}")        
           
    return results["ids"]

def debug_setup(pg_frame_tiles):
    index = 0
    for y in range(0, SIZE_H, TILE_H):
        for x in range(0, SIZE_W, TILE_W):
            py5.push_matrix()
            py5.translate(x, y)
            py5.image(pg_frame_tiles[index], 0, 0, TILE_W, TILE_H)
            py5.pop_matrix()
            index = index+1

def store_matrix(index, matrix):
    logger.info(f"file matrix length: {len(matrix)}")
    vector = []
    for rgba in matrix: #matrix_x * matrix_y length
        vector.append((rgba[0]<< 24) + (rgba[1] << 16) + (rgba[2] << 8) + (rgba[3]))
    #convert each color array into an absolute value
    collection.add(
                embeddings = vector,
                ids=[f"{index}"]
                )
    logger.info("Matrix successfully stored")

def rasterize(pg):
    frame_index = 0
    for y in range(0, SIZE_H, TILE_H):
        for x in range(0, SIZE_W, TILE_W):

            index = euclidean_distance(frame_matrices[frame_index])
            logger.info(f"euclidean distance {index[0][0]}")
            pg.begin_draw()
            pg.push_matrix()
            pg.translate(x, y)
            #Reload file image and place
            file = py5.load_image(FILES[int(index[0][0])])
            pg.image(file, 0, 0, TILE_W, TILE_H)
            pg.pop_matrix()
            pg.end_draw()
            frame_index = frame_index+1

    return pg 

# Function to find the most recent file in a directory
def latest_file(path):
    list_of_files = glob.glob(path) 
    if not list_of_files:  # if list is empty
        return None
    latest_file = max(list_of_files, key=os.path.getctime)
    return latest_file

# Create a Gradio interface
def start_rasterization():
    # Return the path to the latest file in the `data/outputs` folder
    latest_image = latest_file('data/outputs/*')
    return latest_image, gr.update(value=[latest_image, latest_image])  # Example update

# Setting up the Gradio interface
with gr.Blocks() as gradio_interface:
    with gr.Column():
        SIZE_W = gr.Number(label="Width (size_w)", value=3840)
        SIZE_H = gr.Number(label="Height (size_h)", value=2160)
        MATRIX_X = gr.Number(label="Matrix X (matrix_x)", value=8)
        MATRIX_Y = gr.Number(label="Matrix Y (matrix_y)", value=8)
        TILE_X = gr.Number(label="Tile X (tile_x)", value=40)
        TILE_Y = gr.Number(label="Tile Y (tile_y)", value=60)
        start_button = gr.Button("Start Rasterization")
        
    
    output_image = gr.Image(label="Output Image")
    examples = gr.Examples(examples=[f"{FRAMES[0]}.jpg"], inputs=start_button, outputs=output_image, fn=lambda x: x)
    
    start_button.click(
        fn=start_rasterization,
        #inputs=[size_w, size_h, matrix_x, matrix_y, tile_x, tile_y, start_button],
        outputs=output_image
    )           

if __name__ == "__main__":
    py5.run_sketch()
    gradio_interface.launch()