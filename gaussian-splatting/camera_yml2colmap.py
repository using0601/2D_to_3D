import argparse
parser = argparse.ArgumentParser()
parser.add_argument('dataset_name', type=str)
args = parser.parse_args()


import struct
import os

import numpy as np
import PIL.Image
import cv2

from scene.colmap_loader import CAMERA_MODEL_NAMES, Image, Camera, rotmat2qvec


# https://github.com/colmap/colmap/blob/main/scripts/python/read_write_model.py
def write_next_bytes(fid, data, format_char_sequence, endian_character="<"):
    """pack and write to a binary file.
    :param fid:
    :param data: data to send, if multiple elements are sent at the same time,
    they should be encapsuled either in a list or a tuple
    :param format_char_sequence: List of {c, e, f, d, h, H, i, I, l, L, q, Q}.
    should be the same length as the data list or tuple
    :param endian_character: Any of {@, =, <, >, !}
    """
    if isinstance(data, (list, tuple)):
        bytes = struct.pack(endian_character + format_char_sequence, *data)
    else:
        bytes = struct.pack(endian_character + format_char_sequence, data)
    fid.write(bytes)


def write_intrinsics_binary(cameras, path_to_model_file):
    with open(path_to_model_file, "wb") as fid:
        write_next_bytes(fid, len(cameras), "Q")
        for _, cam in cameras.items():
            model_id = CAMERA_MODEL_NAMES[cam.model].model_id
            camera_properties = [cam.id,
                                 model_id,
                                 cam.width,
                                 cam.height]
            write_next_bytes(fid, camera_properties, "iiQQ")
            for p in cam.params:
                write_next_bytes(fid, float(p), "d")
    return cameras


def write_extrinsics_binary(images, path_to_model_file):
    with open(path_to_model_file, "wb") as fid:
        write_next_bytes(fid, len(images), "Q")
        for _, img in images.items():
            write_next_bytes(fid, img.id, "i")
            write_next_bytes(fid, img.qvec.tolist(), "dddd")
            write_next_bytes(fid, img.tvec.tolist(), "ddd")
            write_next_bytes(fid, img.camera_id, "i")
            for char in img.name:
                write_next_bytes(fid, char.encode("utf-8"), "c")
            write_next_bytes(fid, b"\x00", "c")
            write_next_bytes(fid, len(img.point3D_ids), "Q")
            for xy, p3d_id in zip(img.xys, img.point3D_ids):
                write_next_bytes(fid, [*xy, p3d_id], "ddq")


dataset_path = os.path.join('dataset', args.dataset_name)
cam_path = os.path.join(dataset_path, 'sparse', '0')
os.makedirs(cam_path, exist_ok=True)

intri = cv2.FileStorage(os.path.join(dataset_path, 'intri.yml'),
                        cv2.FILE_STORAGE_READ)
extri = cv2.FileStorage(os.path.join(dataset_path, 'extri.yml'),
                        cv2.FILE_STORAGE_READ)

names = intri.getNode('names')
Camera_list = []
for i in range(names.size()):
    Camera_name = names.at(i).string()
    if Camera_name.startswith('Camera_B'):
        Camera_list.append(Camera_name)
length = len(Camera_list)

cam_intrinsics, cam_extrinsics = {}, {}

for i in range(length):
    name = 'Camera_B{}.png'.format(i + 1)
    with PIL.Image.open(os.path.join(dataset_path, 'images', name)) as im:
        width, height = im.size

    cameraMatrix = intri.getNode('K_Camera_B{}'.format(i + 1)).mat()
    cam_intrinsics[i + 1] = Camera(
        id=i+1, model='PINHOLE', width=width, height=height,
        params=cameraMatrix[[0, 1, 0, 1], [0, 1, 2, 2]]
    )
    cam_extrinsics[i + 1] = Image(
        id=i+1,
        qvec=rotmat2qvec(
            extri.getNode('Rot_Camera_B{}'.format(i + 1)).mat()),
        tvec=extri.getNode(
            'T_Camera_B{}'.format(i + 1)).mat()[:, 0],
        camera_id=i+1, name=name, xys=np.empty((0, 2)),
        point3D_ids=np.empty(0, dtype=int)
    )

write_intrinsics_binary(cam_intrinsics, os.path.join(cam_path, 'cameras.bin'))
write_extrinsics_binary(cam_extrinsics, os.path.join(cam_path, 'images.bin'))
