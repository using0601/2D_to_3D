import os
import json
import numpy as np
import open3d as o3d
from tqdm import tqdm

def main(dataset_name):
    path = os.path.join("generate_pointcloud", "output", dataset_name, "vertices")
    os.makedirs(os.path.join("generate_pointcloud", "pcd", dataset_name), exist_ok = True)

    files = os.listdir(path)
    for filename in files:
        file_path = os.path.join(path, filename)
        f = open(file_path)
        data = json.load(f)
        xyz = np.array(data[0]["vertices"])
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(xyz)

        o3d.io.write_point_cloud(os.path.join("generate_pointcloud", "pcd", dataset_name, filename.replace('.json', '.ply')), pcd)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('dataset_name', type=str)
    args = parser.parse_args()
    main(args.dataset_name)