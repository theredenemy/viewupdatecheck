import srctools.vtf as vtf
from srctools.keyvalues import Keyvalues
from srctools.vmt import Material


import os
from pathlib import Path
import shutil


def vtf_to_video(input_vtf, input_vmt, input_wav, output):
    path = os.path.dirname(output)
    print(path)
    frames_dir = os.path.join(path, "frames")
    print()
    if os.path.isdir(frames_dir):
        shutil.rmtree(frames_dir)
    os.makedirs(frames_dir)
    with open(input_vmt, 'r') as f:
        kv = Keyvalues.parse(f)
        root = next(iter(kv))
        fps = 12
        proxies = root.find_key("Proxies", None)
        if proxies:
            animated = root.find_key("AnimatedTexture", None)
            if animated:
                fps = root.find_key("animatedTextureFrameRate", "12").value

    with open(input_vtf, 'rb') as f:
        vtf_data = vtf.VTF.read(f)
        width, height = vtf_data.width, vtf_data.height
        frame_count = vtf_data.frame_count


    with open(input_vtf, 'rb') as f:
        vtf_data = vtf.VTF.read(f)
        for i in range(frame_count):
            vtf_frame = vtf_data.get(frame=i)
            img = vtf_frame.to_PIL().convert('RGB')
            save_img_path = os.path.join(frames_dir, f"{Path(input_vtf).stem}_{i:04d}.png")
            img.save(save_img_path)
    os.system(f'ffmpeg -framerate {fps} -i {os.path.join(frames_dir, f"{Path(input_vtf).stem}_%04d.png")} -i {input_wav} -filter:a "atempo=2.0" {output}')