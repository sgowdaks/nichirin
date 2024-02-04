#!/bin/bash

# Get the file path from the user
echo "Enter the file path:"
read file_path

# Check if the file exists
if [ ! -f "$file_path" ]; then
    echo "File not found!"
    exit 1
fi

# Get the file size in bytes
file_size=$(du -b "$file_path" | cut -f1)

# Print the file size
echo "Size of $file_path is $file_size bytes."

# Partition the file
# Here, we're creating partitions of size 1K. Adjust as needed.
split -b 1024 "$file_path" "part-"

echo "Partitioning completed. Files are named as part-aa, part-ab, etc."

# Remove the original file
rm "$file_path"

echo "Original file removed."
