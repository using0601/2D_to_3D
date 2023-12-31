import os
import shutil

def main(dataset_name, time_step):

    dir_path = os.path.join("dataset", dataset_name, "images")

    entries = os.listdir(dir_path)

    # Filter out only the directories
    directories = [entry for entry in entries if os.path.isdir(os.path.join(dir_path, entry))]

    for dir in directories:
        file_dir = os.path.join(dir_path, dir, time_step)
        if os.path.exists(file_dir + ".png"):
            shutil.copyfile(file_dir + ".png", os.path.join(dir_path, dir + ".png"))
        elif os.path.exists(file_dir + ".jpg"):
            shutil.copyfile(file_dir + ".jpg", os.path.join(dir_path, dir + ".jpg"))
        else:
            print(f'The file "{file_dir + ".png"}" is not found')

    sparse_path = os.path.join("dataset", dataset_name, "sparse", "0")
    os.makedirs(sparse_path, exist_ok=True)
    shutil.copyfile(
        os.path.join("generate_pointcloud", "pcd", dataset_name, time_step + ".ply"),
        os.path.join(sparse_path, "points3D.ply"))



if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('dataset_name', type=str)
    parser.add_argument('time_step', type=str)
    args = parser.parse_args()
    main(args.dataset_name, args.time_step)