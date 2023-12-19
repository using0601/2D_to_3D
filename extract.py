import os

def main(dataset_name, time_step):

    dir_path = os.path.join("dataset", dataset_name, "images")

    entries = os.listdir(dir_path)

    # Filter out only the directories
    directories = [os.path.join(entry, time_step) for entry in entries if os.path.isdir(os.path.join(dir_path, entry))]
    
    print(directories)



if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('dataset_name', type=str)
    parser.add_argument('time_step', type=str)
    args = parser.parse_args()
    main(args.dataset_name, args.time_step)