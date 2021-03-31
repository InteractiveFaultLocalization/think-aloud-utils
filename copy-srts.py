import argparse
import shutil
import os
import glob2

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=str, required=True)
    parser.add_argument('--target', type=str, required=True)
    args = parser.parse_args()

    if not os.path.isdir(args.source):
        print("source is not a directory")
    if not os.path.isdir(args.target):
        print("target is not a directory")

    sub_folder: os.DirEntry
    for sub_folder in os.scandir(args.source):
        if sub_folder.is_dir():
            parts = os.path.split(sub_folder.path)
            participant = parts[-1].split('-')[-1]
            out_path = os.path.join(args.target, participant)
            if not os.path.isdir(out_path):
                os.mkdir(out_path)
            print("copy to: " + out_path)
            file: os.DirEntry
            for file in os.scandir(sub_folder):
                if file.is_file() and file.path.endswith('.srt'):
                    target_file = os.path.join(out_path, os.path.basename(file.path))
                    print("copy as: " + target_file)
                    shutil.copy(file.path, target_file)
                    print("copied")
            print()
