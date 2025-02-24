def remove_urls(file1_path, file2_path, output_file_path):
    """
    Removes URLs from file1 that are present in file2 and writes the result to an output file.

    Args:
        file1_path (str): Path to the first file containing URLs.
        file2_path (str): Path to the second file containing URLs to remove.
        output_file_path (str): Path to the output file to store the filtered URLs.
    """
    try:
        with open(file2_path, "r") as file2:
            urls_to_remove = set(line.strip() for line in file2)

        filtered_urls = []
        with open(file1_path, "r") as file1:
            for line in file1:
                url = line.strip()
                if url not in urls_to_remove:
                    filtered_urls.append(url)

        with open(output_file_path, "w") as output_file:
            for url in filtered_urls:
                output_file.write(url + "\n")

        print(f"URLs filtered and saved to {output_file_path}")

    except FileNotFoundError:
        print("Error: One or both input files not found.")
    except Exception as e:
        print(f"An error occurred: {e}")


# Example usage:
file1_path = "output-f.txt"  # Replace with the actual path to your first file
file2_path = "file3.txt"  # Replace with the actual path to your second file
output_file_path = "output-fv.txt"  # Replace with your desired output file name.

remove_urls(file1_path, file2_path, output_file_path)
