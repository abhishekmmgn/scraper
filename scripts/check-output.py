def check_urls_in_output(file2_path, output_file_path):
    """
    Checks if any URLs from file2 are present in the output file.

    Args:
        file2_path (str): Path to the file containing URLs to check.
        output_file_path (str): Path to the output file to scan.
    """
    try:
        # Load URLs to check into a set (assuming file2 is relatively small)
        with open(file2_path, "r") as file2:
            urls_to_check = set(line.strip() for line in file2)

        found_urls = set()
        # Scan the output file line by line to check for membership
        with open(output_file_path, "r") as output_file:
            for line in output_file:
                url = line.strip()
                if url in urls_to_check:
                    found_urls.add(url)

        if found_urls:
            print("The following URLs from file2 were found in the output file:")
            for url in found_urls:
                print(url)
        else:
            print("No URLs from file2 were found in the output file.")

    except FileNotFoundError:
        print("Error: One or both files not found.")
    except Exception as e:
        print(f"An error occurred: {e}")


# Example usage:
file2_path = "file1.txt"  # Replace with your file2 path
output_file_path = "file2.txt"  # Replace with your output file path

check_urls_in_output(file2_path, output_file_path)
