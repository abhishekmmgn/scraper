import re


def filter_lines_with_url(input_file, output_file, url_pattern):
    try:
        with open(input_file, "r") as file:
            lines = file.readlines()

        # Filter lines that match the URL pattern and have the required format
        filtered_lines = [line for line in lines if re.match(url_pattern, line)]

        with open(output_file, "w") as file:
            file.writelines(filtered_lines)

        print(f"Filtered lines have been written to {output_file}")

    except FileNotFoundError:
        print(f"The file {input_file} does not exist.")
    except Exception as e:
        print(f"An error occurred: {e}")


# Usage
input_file = "filtered-hotels.txt"  # The output file from the previous step
output_file = "hotel-details.txt"
url_pattern = r"https://www\.travelweekly\.com/Hotels/[^/]+/[^/]+-p\d+"

filter_lines_with_url(input_file, output_file, url_pattern)
