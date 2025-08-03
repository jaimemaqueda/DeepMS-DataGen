import os
import json
import h5py

def update_train_val_test_split(input_file, root_dir, output_file):
    # Load the existing train/val/test split JSON file
    with open(input_file, 'r') as f:
        split_data = json.load(f)
    
    # Create new dictionaries to store the updated train, validation, and test sets
    new_split_data = {
        "train": [],
        "validation": [],
        "test": []
    }
    
    # Function to process each set and update the split data
    def process_set(set_name):
        for sample in split_data[set_name]:
            folder, filename = sample.split('/')
            h5_file_path = os.path.join(root_dir, folder, f"{filename}.h5")
            
            # Open the .h5 file and read the length of the "operations" array
            try:
                with h5py.File(h5_file_path, 'r') as h5_file:
                    operations = h5_file["operations"]
                    length = len(operations)
                    
                    # Create new samples with indices from 00 to (length - 1)
                    for i in range(length - 1):
                        new_sample = f"{folder}/{filename}/{str(i).zfill(2)}"
                        new_split_data[set_name].append(new_sample)
            
            except Exception as e:
                print(f"Error processing file {h5_file_path}: {e}")
    
    # Process train, validation, and test sets
    process_set("train")
    process_set("validation")
    process_set("test")
    
    # Save the updated split data to a new JSON file
    with open(output_file, 'w') as f:
        json.dump(new_split_data, f, indent=4)
    
    print(f"Updated Train/Validation/Test split saved to {output_file}")

# Example usage
if __name__ == "__main__":
    update_train_val_test_split(
        input_file='C:/Users/jgomez310/Documents/data_deepms/train_val_test_split.json',
        root_dir='C:/Users/jgomez310/Documents/data_deepms/seq_h5',
        output_file='C:/Users/jgomez310/Documents/data_deepms/train_val_test_split_voxels.json'
    )