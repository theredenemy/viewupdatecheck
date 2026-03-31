                                                                                                 
import requests
import configHelper
import os
import dateutil
import traceback
import time
import shutil
import winsound
import pygame
import obsws_python as obs
import threading

timeout = 10
config_file = "view.ini"
maindir = os.getcwd()
view_dir = "views"
updated_files = []
threads = []
use_obs = False
if use_obs:
    while True:
        try:
            cl = obs.ReqClient(host="localhost", port=4455)
            break
        except Exception as e:
            print(type(e).__name__)
            error = traceback.format_exc()
            print(error)
scene_name = "VIEW"
scene_item_name = "VIEW_UPDATE"

def ViewUpdate():
    if not use_obs:
        return False
    resp = cl.get_scene_item_list(scene_name)
    scene_items = [item['sourceName'] for item in resp.scene_items]
    if not scene_item_name in scene_items:
        return False
        
    resp = cl.get_scene_item_id(scene_name, scene_item_name)
    item_id = resp.scene_item_id
    cl.set_scene_item_enabled(scene_name, item_id, True)
    time.sleep(1)
    cl.set_scene_item_enabled(scene_name, item_id, False)

pygame.mixer.init(devicename="CABLE Input (VB-Audio Virtual Cable)")

fastdl = "https://myserver06.ca.eu.org/fastdl/tf2"

materials = ['view.vtf', 'view.vmt']
sounds = ['view.wav']

#last_updated = configHelper.read_config(config_file, filename, "last_updated", is_float=True)
def download_file(url, filename):
    file_data = requests.get(url, allow_redirects=True)
    open(filename, 'wb').write(file_data.content)
    return filename
def check_file_url(url, filename):
    last_updated = configHelper.read_config(config_file, filename.replace('.', ''), "last_updated", is_float=True)
    print(f"Checking: {url}")
    file_date = get_file_date(url)
    if not file_date:
        return
    if not file_date == last_updated:
        print(f"UPDATE: {url}")
        updated_files.append(filename)
        download_file(url, filename)
        configHelper.set_config(config_file, filename.replace('.', ''), "last_updated", file_date)
    else:
        print(f"OK: {url}")
    return
def get_file_date(url):
    try:
        header = requests.head(url)
        if header.status_code == 200:
            date_string = header.headers.get('Last-Modified')
            dt = dateutil.parser.parse(date_string)
            unix_time = dt.timestamp()
            return unix_time
        else:
            return False
    except Exception as e:
        print(type(e).__name__)
        error = traceback.format_exc()
        print(error)
        return False

def main():
    updated_files = []
    threads = []
    ts = int(time.time())
    if use_obs:
        cl.set_current_program_scene(scene_name)
    print("Wait")
    time.sleep(timeout)
    for material in materials:
        url = f"{fastdl}/materials/{material}"
        t = threading.Thread(target=check_file_url, kwargs={"url": url, "filename": material})
        threads.append(t)
        
    for sound in sounds:
        url = f"{fastdl}/sound/{sound}"
        t = threading.Thread(target=check_file_url, kwargs={"url": url, "filename": sound})
        threads.append(t)
    for t in threads:
        t.start()
    for t in threads:
        t.join()
        threads.remove(t)
    time.sleep(1)
    list_len = 0
    for item in updated_files:
        list_len += 1
    print(list_len)
    if list_len > 0:
        print("NEW VIEW")
        pygame.mixer.music.load("skybox_alert.wav")
        pygame.mixer.music.play()
        winsound.PlaySound("skybox_alert.wav", winsound.SND_FILENAME)
        if os.path.isfile("note.cmd"):
            os.system("start cmd /c note.cmd")
        view_data_dir = os.path.join(maindir, view_dir, str(ts))
        if not os.path.isdir(view_dir):
            os.mkdir(view_dir)
        if not os.path.isdir(view_data_dir):
            os.mkdir(view_data_dir)
        for file in updated_files:
            shutil.move(file, view_data_dir)
        if use_obs:
            for i in range(5):
                ViewUpdate()
                time.sleep(1)
    else:
        print("No New View")

if __name__ == '__main__':
    while True:
        try:
            main()
        except Exception as e:
            print(type(e).__name__)
            error = traceback.format_exc()
            print(error)






        