from logutils import get_logger
logger = get_logger("files_utils")
#due to the py5 library constrain
from PIL import Image
import os
import time
import psutil
import glob
FILES_PATH = glob.glob("data/downloads_second_batch/*")

def sanitize_files(FILES_PATH, max_attempts=4, wait_seconds=1):
    deletion_queue = []
    def analize():
        for file in FILES_PATH:
            logger.info(file)
            with Image.open(file) as img:
                logger.info(f"{img.width}, {img.height}")
                if img.width < 25 or img.height < 25:
                    deletion_queue.append(file)
    def delete():             
        for file in deletion_queue:
            attempt = 1
            while attempt <= max_attempts:
                    try:
                        os.remove(file)
                        logger.info(f"Successfully deleted: {file}")
                        break
                    except PermissionError as e:
                        logger.info(f"Attempt {attempt} failed: {e}")
                        unlock_process(file)
                        logger.info("Unlocking process failed")
                        time.sleep(wait_seconds)
                        attempt += 1
            else:
                logger.info(f"Failed to delete {file} after {max_attempts} attempts.")
                exit()                         
    analize()
    delete()                

def unlock_process(locked_file_path):
    for process in psutil.process_iter(['open_files']):
        if process.info['open_files']:
            for file in process.info['open_files']:
                if file.path == locked_file_path:
                    logger.info(f"Found locking process: {process.pid} - {process.name()}")
                    # Attempt to terminate the process
                    process.terminate()
                    logger.info(f"Terminated process {process.pid}")
                    break    

if __name__ == "__main__":
    sanitize_files(FILES_PATH)