import re


def remove_spaces_from_urls(input_file, output_file):
    """
    Reads URLs from an input file, removes spaces within the URLs,
    and writes the corrected URLs to an output file.

    Args:
        input_file (str): Path to the input file containing URLs.
        output_file (str): Path to the output file to store corrected URLs.
    """
    try:
        with open(input_file, "r") as infile, open(output_file, "w") as outfile:
            for line in infile:
                url = line.strip()  # Remove leading/trailing whitespace

                # Use regular expression to find and replace spaces within URLs.
                # This regex looks for spaces after the protocol (http/https)
                # and before any potential query parameters or fragments.
                corrected_url = re.sub(r"(https?://[^?#\s]*)\s+", r"\1", url)

                outfile.write(corrected_url + "\n")

        print(f"URLs corrected and saved to {output_file}")

    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")


# Example Usage:
input_file_path = "file2.txt"  # Replace with your input file
output_file_path = "file3.txt"  # Replace with your output file

remove_spaces_from_urls(input_file_path, output_file_path)
