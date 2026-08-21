                                                                                                 
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
from vtf_to_video import vtf_to_video
from pathlib import Path

timeout = 10
view_times = "view.ini"
config_file = "config.ini"
maindir = os.getcwd()
view_dir = "views"
updated_files = []
threads = []
use_obs = configHelper.read_config(config_file, "Config", "use_obs", False, is_bool=True)
use_audio_device = configHelper.read_config(config_file, "Config", "use_audio_device", False, is_bool=True)
audio_device = configHelper.read_config(config_file, "Config", "audio_device", "CABLE Input (VB-Audio Virtual Cable)")

if use_obs:
    try:
        cl = obs.ReqClient(host="localhost", port=4455)
        use_obs = True
    except ConnectionRefusedError:
        use_obs = False
scene_name = None
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
if use_audio_device:
    pygame.mixer.init(devicename=audio_device)

fastdl = configHelper.read_config(config_file, "Config", "fastdl", "https://myserver06.ca.eu.org/fastdl/tf2")

materials = ['view.vtf', 'view.vmt']
sounds = ['view.wav']

#last_updated = configHelper.read_config(config_file, filename, "last_updated", is_float=True)
def download_file(url, filename):
    file_data = requests.get(url, allow_redirects=True)
    open(filename, 'wb').write(file_data.content)
    return filename
def check_file_url(url, filename):
    global updated_files
    last_updated = configHelper.read_config(view_times, filename.replace('.', ''), "last_updated", is_float=True)
    print(f"Checking: {url}")
    for i in range(5):
        file_date = get_file_date(url)
    if not file_date:
        return
    if not file_date == last_updated:
        print(f"UPDATE: {url}")
        updated_files.append(filename)
        download_file(url, filename)
        configHelper.set_config(view_times, filename.replace('.', ''), "last_updated", file_date)
    else:
        print(f"OK: {url}")
    return
def get_file_date(url):
    try:
        header = requests.head(url, timeout=timeout)
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
    global scene_name
    threads = []
    ts = int(time.time())
    if use_obs:
        scene_name = cl.get_current_program_scene().scene_name
    print("Wait")
    time.sleep(timeout)
    for file in materials:
        url = f"{fastdl}/materials/{file}"
        t = threading.Thread(target=check_file_url, kwargs={"url": url, "filename": file})
        threads.append(t)
        
    for file in sounds:
        url = f"{fastdl}/sound/{file}"
        t = threading.Thread(target=check_file_url, kwargs={"url": url, "filename": file})
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
        if use_audio_device:
            pygame.mixer.music.load("skybox_alert.wav")
            pygame.mixer.music.play()
        winsound.PlaySound("skybox_alert.wav", winsound.SND_FILENAME)
        for file in materials:
            if not file in updated_files:
                url = f"{fastdl}/materials/{file}"
                last_updated = configHelper.read_config(view_times, file.replace('.', ''), "last_updated", is_float=True)
                print(f"Checking: {url}")
                for i in range(5):
                    file_date = get_file_date(url)
                if not file_date:
                    continue
                if not file_date == last_updated:
                    if use_audio_device:
                        pygame.mixer.music.load("skybox_alert.wav")
                        pygame.mixer.music.play()
                    winsound.PlaySound("skybox_alert.wav", winsound.SND_FILENAME)
                    print(f"UPDATE: {url}")
                    updated_files.append(file)
                    download_file(url, file)
                    configHelper.set_config(view_times, file.replace('.', ''), "last_updated", file_date)
                else:
                    print(f"OK: {url}")
        for file in sounds:
            if not file in updated_files:
                url = f"{fastdl}/sound/{file}"
                last_updated = configHelper.read_config(view_times, file.replace('.', ''), "last_updated", is_float=True)
                print(f"Checking: {url}")
                for i in range(5):
                    file_date = get_file_date(url)
                if not file_date:
                    continue
                if not file_date == last_updated:
                    print(f"UPDATE: {url}")
                    if use_audio_device:
                        pygame.mixer.music.load("skybox_alert.wav")
                        pygame.mixer.music.play()
                    winsound.PlaySound("skybox_alert.wav", winsound.SND_FILENAME)
                    updated_files.append(file)
                    download_file(url, file)
                    configHelper.set_config(view_times, file.replace('.', ''), "last_updated", file_date)
                else:
                    print(f"OK: {url}")
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
        for file in materials:
            join_file = os.path.join(view_data_dir, file)
            url = f"{fastdl}/materials/{file}"
            if not os.path.isfile(join_file):
                download_file(url, join_file)

        for file in sounds:
            join_file = os.path.join(view_data_dir, file)
            url = f"{fastdl}/sound/{file}"
            if not os.path.isfile(join_file):
                download_file(url, join_file)
        vtf, vmt, *rest = materials
        wav, *rest = sounds
        
        vtf_to_video(os.path.join(view_data_dir, vtf), os.path.join(view_data_dir, vmt), os.path.join(view_data_dir, wav), os.path.join(view_data_dir, f"{Path(vtf).stem}.mp4"))
    else:
        print("No New View")

if __name__ == '__main__':
    while True:
        try:
            updated_files = []
            main()
        except Exception as e:
            print(type(e).__name__)
            error = traceback.format_exc()
            print(error)






        