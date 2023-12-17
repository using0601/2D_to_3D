from colmap_loader import *
import cv2
import os

def main(dataset_name):
    # Extrinsic
    fs = cv2.FileStorage(os.path.join("dataset", dataset_name, "extri.yml"), cv2.FILE_STORAGE_WRITE)
    extri = read_extrinsics_binary(os.path.join("dataset", dataset_name, "comap_cam", "images.bin"))

    length = len(extri)

    Camera_list = []
    for i in range(length):
        Camera_list.append(f'Camera_B{i+1}')
    fs.write('names', Camera_list)

    for i in range(length):
        rot = qvec2rotmat(extri[i+1].qvec)
        fs.write(f'Rot_Camera_B{i+1}', rot)
        fs.write(f'T_Camera_B{i+1}', extri[i+1].tvec)
        fs.write(f'R_Camera_B{i+1}', cv2.Rodrigues(rot)[0])

    fs.release()

    # Intrinsic
    fs = cv2.FileStorage(os.path.join("dataset", dataset_name, "intri.yml"), cv2.FILE_STORAGE_WRITE)
    intri = read_intrinsics_binary(os.path.join("dataset", dataset_name, "comap_cam", "cameras.bin"))
    intri_params = intri[1].params

    Camera_list = []
    for i in range(length):
        Camera_list.append(f'Camera_B{i+1}')
    fs.write('names', Camera_list)

    for i in range(length):
        m = np.zeros((3,3))
        m[0][0] = intri_params[0]
        m[1][1] = intri_params[1]
        m[0][2] = intri_params[2]
        m[1][2] = intri_params[3]
        m[2][2] = 1
        fs.write(f'K_Camera_B{i+1}', m)

        dist = np.zeros((1,5))
        dist[0, 0:4] = intri_params[4:8]
        fs.write(f'dist_Camera_B{i+1}', dist)

    fs.release()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('dataset_name', type=str)
    args = parser.parse_args()
    main(args.dataset_name)