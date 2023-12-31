import os
import shutil

def main(dataset_name, time_step, skip_image, skip_pcd):

    image_path = os.path.join("dataset", dataset_name, "images")
    mask_path = os.path.join("dataset", dataset_name, "mask")
    sparse_path = os.path.join("dataset", dataset_name, "sparse", "0")

    if not skip_image:
        import numpy as np
        from PIL import Image

        entries = os.listdir(image_path)

        # Filter out only the directories
        directories = [entry for entry in entries if os.path.isdir(os.path.join(image_path, entry))]

        for dir in directories:
            file_dir = os.path.join(image_path, dir, time_step)
            if os.path.exists(file_dir + ".png"):
                with Image.open(file_dir + ".png") as im:
                    imdata = np.asarray(im)
            elif os.path.exists(file_dir + ".jpg"):
                with Image.open(file_dir + ".jpg") as im:
                    imdata = np.asarray(im)
            else:
                print(f'The file "{file_dir + ".png"}" is not found')
                continue

            with Image.open(os.path.join(mask_path, dir, time_step) + ".png") as im:
                mask = np.asarray(im)
            imdata = np.dstack((imdata * np.atleast_3d(mask), mask * 255))
            Image.fromarray(imdata).save(os.path.join(image_path, dir + ".png"))

    if not skip_pcd:
        os.makedirs(sparse_path, exist_ok=True)
        shutil.copyfile(
            os.path.join("generate_pointcloud", "pcd", dataset_name, time_step + ".ply"),
            os.path.join(sparse_path, "points3D.ply"))



if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('dataset_name', type=str)
    parser.add_argument('time_step', type=str)
    parser.add_argument("--skip_image", action="store_true")
    parser.add_argument("--skip_pcd", action="store_true")
    args = parser.parse_args()
    main(args.dataset_name, args.time_step, args.skip_image, args.skip_pcd)