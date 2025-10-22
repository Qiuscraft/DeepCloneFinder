import os
import sys

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import dataset_path
from tqdm import tqdm
from multiprocessing import Pool, cpu_count

def count_lines_in_file(file_path):
    """Counts the number of lines in a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return len(f.readlines())
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return 0

def count_lines_in_directory(directory):
    """Counts the total number of lines in all files within a directory."""
    java_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            # We only count lines for .java files, as this is a java dataset.
            if file.endswith(".java"):
                java_files.append(os.path.join(root, file))

    with Pool(processes=cpu_count()) as pool:
        results = list(tqdm(pool.imap_unordered(count_lines_in_file, java_files), total=len(java_files), desc="Counting lines"))

    total_lines = sum(results)
    return total_lines

if __name__ == "__main__":
    # The dataset_path in config.py is relative to the project root.
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    absolute_dataset_path = os.path.abspath(os.path.join(project_root, dataset_path))

    if not os.path.exists(absolute_dataset_path):
        print(f"Error: Dataset path not found at {absolute_dataset_path}")
    else:
        print(f"Counting lines of code in: {absolute_dataset_path}")
        total_line_count = count_lines_in_directory(absolute_dataset_path)
        print(f"Total lines of code in .java files: {total_line_count}")
