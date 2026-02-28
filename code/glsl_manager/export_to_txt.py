
import os

# Define which file extensions to include
INCLUDE_EXTENSIONS = {'.py', '.glsl', '.txt', '.md'}

# Output file name
OUTPUT_FILE = 'combined_output.txt'

def collect_files(base_dir):
    """Recursively collect files with target extensions."""
    collected = []
    for root, _, files in os.walk(base_dir):
        for file in files:
            if os.path.splitext(file)[1] in INCLUDE_EXTENSIONS:
                collected.append(os.path.join(root, file))
    return collected

def write_combined_output(files, output_path):
    """Write contents of all files into one output file."""
    with open(output_path, 'w', encoding='utf-8') as out:
        for file_path in files:
            out.write(f"\n{'='*40}\n{file_path}\n{'='*40}\n")
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    out.write(f.read())
            except Exception as e:
                out.write(f"[Error reading {file_path}: {e}]\n")

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    subfolder = os.path.join(current_dir)  # or specify a subfolder like 'src'
    files = collect_files(subfolder)
    write_combined_output(files, os.path.join(current_dir, OUTPUT_FILE))
    print(f"✅ Combined {len(files)} files into {OUTPUT_FILE}")