import os

def main(dataset_name, time_step):

    dir_path = os.path.join("dataset", dataset_name, "images")

    entries = os.listdir(dir_path)

    # Filter out only the directories
    directories = [os.path.join(entry, time_step) for entry in entries if os.path.isdir(os.path.join(dir_path, entry))]
    output = []

    for dir in directories:
        file_path = os.path.join(dir_path, dir) + ".png"
        if os.path.exists(file_path):
            output.append(dir + ".png")
        elif os.path.exists(file_path.replace(".png", ".jpg")):
            output.append(dir + ".jpg")
        else:
            print(f'The file "{file_path}" is not found')

    # print("output:", output)



if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('dataset_name', type=str)
    parser.add_argument('time_step', type=str)
    args = parser.parse_args()
    main(args.dataset_name, args.time_step)