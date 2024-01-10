import argparse
parser = argparse.ArgumentParser()
parser.add_argument('dataset_name', type=str)
args = parser.parse_args()


import struct
import os

import numpy as np
import PIL.Image
import cv2

from scene.colmap_loader import (
    CAMERA_MODEL_NAMES, Image, Camera, rotmat2qvec,
    write_intrinsics_binary, write_extrinsics_binary)


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
