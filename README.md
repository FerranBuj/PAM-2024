# Requirements
chromadb & py5 libraries. You can refer to the official py5 documentation the the installation of the latter. 
# Retrieval Augmented Rasterization 

<h3>1.Set a resolution and a grid size in the config.json file</h3>
<h3>2.Add image files in the data/input folder</h3>
<h3>3.Add frames to process in the data/frames folder</h3>
<h3>4.Run with "python main.py"</h3>

# How it works:

Each frame is tiled into a grid of x * y tiles and each input image is resized to the size of the frame tiles. The program then computes a vector representing the average colors on each frame and image tile and stores it in a vector database using the chromadb library. Finally, the program compares the vectors of the former frame tiles with the available images, choosing the file with a smaller euclidean distance.

    
    j= subtile_index
    frame tile        file image tile[]   
        ___________       ___________                     ____         ____
    |j0|__|__|__| --> |j0|__|__|__|  --> distance += j0-n|rgba| - j0-n|rgba| 
    |__|__|__|__|     |__|__|__|__|        
    |__|__|__|__|     |__|__|__|__|
    |__|__|__|jn|     |__|__|__|jn|
      
