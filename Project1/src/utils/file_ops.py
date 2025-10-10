import os
import time


def rename_latest_file(download_dir, new_name):
    time.sleep(2)
    files = sorted(os.listdir(download_dir), key=lambda x: os.path.getctime(os.path.join(download_dir, x)), reverse=True)
    latest_file = files[0]
    os.rename(os.path.join(download_dir, latest_file), os.path.join(download_dir, new_name))
