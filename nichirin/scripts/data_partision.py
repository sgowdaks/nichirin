import os
from pathlib import Path

# Get the file path from the user
file_path = input("Enter the file path: ")

# Check if the file exists
if not Path(file_path).is_file():
    print("File not found!")
    exit(1)

# Get the file size in bytes
file_size = Path(file_path).stat().st_size

# Print the file size
print(f"Size of {file_path} is {file_size} bytes.")

# Partition the file
# Here, we're creating partitions of size 1K. Adjust as needed.
with open(file_path, 'rb') as f:
    i = 0
    while chunk := f.read(1024):
        with open(f"part-{i:02}", 'wb') as f_part:
            f_part.write(chunk)
        i += 1

print("Partitioning completed. Files are named as part-00, part-01, etc.")

# Remove the original file
os.remove(file_path)

print("Original file removed.")
