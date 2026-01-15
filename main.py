
import requests
import configHelper
import os
import dateutil
import traceback
import time
import shutil
import winsound

timeout = 10
config_file = "view.ini"
maindir = os.getcwd()
view_dir = "views"

fastdl = "https://myserver06.ca.eu.org/fastdl/tf2"

materials = ['view.vtf', 'view.vmt']
sounds = ['view.wav']

#last_updated = configHelper.read_config(config_file, filename, "last_updated", is_float=True)
def download_file(url, filename):
    file_data = requests.get(url, allow_redirects=True)
    open(filename, 'wb').write(file_data.content)
    return filename

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
    ts = int(time.time())
    print("Wait")
    time.sleep(timeout)
    for material in materials:
        url = f"{fastdl}/materials/{material}"
        last_updated = configHelper.read_config(config_file, material.replace('.', ''), "last_updated", is_float=True)
        print(f"Checking: {url}")
        file_date = get_file_date(url)
        if not file_date:
            continue
        if not file_date == last_updated:
            print(f"UPDATE: {url}")
            updated_files.append(material)
            download_file(url, material)
            configHelper.set_config(config_file, material.replace('.', ''), "last_updated", file_date)
        else:
            print(f"OK: {url}")
        time.sleep(1)
    for sound in sounds:
        url = f"{fastdl}/sound/{sound}"
        last_updated = configHelper.read_config(config_file, sound.replace('.', ''), "last_updated", is_float=True)
        print(f"Checking: {url}")
        file_date = get_file_date(url)
        if not file_date:
            continue
        if not file_date == last_updated:
            print(f"UPDATE: {url}")
            updated_files.append(sound)
            download_file(url, sound)
            configHelper.set_config(config_file, sound.replace('.', ''), "last_updated", file_date)
        else:
            print(f"OK: {url}")
        time.sleep(1)
    list_len = 0
    for item in updated_files:
        list_len += 1
    print(list_len)
    if list_len > 0:
        print("NEW VIEW")
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






        