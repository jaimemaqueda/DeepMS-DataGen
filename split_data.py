import os
import random
import json

def create_train_val_test_split(root_dir, output_file, train_ratio=0.9, val_ratio=0.05, test_ratio=0.05):
    assert train_ratio + val_ratio + test_ratio == 1, "The sum of train, validation, and test ratios must be 1."

    # Step 1: Collect all file paths
    all_files = []
    for subdir in os.listdir(root_dir):
        subdir_path = os.path.join(root_dir, subdir)
        if os.path.isdir(subdir_path):
            for file in os.listdir(subdir_path):
                file_path = subdir + "/" + os.path.splitext(file)[0]
                all_files.append(file_path)

    # Step 2: Shuffle the files and split them
    random.shuffle(all_files)
    total_files = len(all_files)

    train_split = int(train_ratio * total_files)
    val_split = train_split + int(val_ratio * total_files)

    train_files = all_files[:train_split]
    val_files = all_files[train_split:val_split]
    test_files = all_files[val_split:]

    # Step 3: Save the split data to a JSON file
    split_data = {
        "train": train_files,
        "validation": val_files,
        "test": test_files
    }

    with open(output_file, 'w') as json_file:
        json.dump(split_data, json_file, indent=4)

    print(f"{total_files} files Train/Validation/Test split saved to {output_file}")

# Example usage
if __name__ == "__main__":
    create_train_val_test_split(root_dir='C:/Users/jgomez310/Documents/data_deepms/seq_h5', output_file='C:/Users/jgomez310/Documents/data_deepms/train_val_test_split.json')