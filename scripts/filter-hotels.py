def filter_lines_with_url(input_file, output_file, url):
    try:
        with open(input_file, "r") as file:
            lines = file.readlines()

        filtered_lines = [line for line in lines if url not in line]

        with open(output_file, "w") as file:
            file.writelines(filtered_lines)

        print(f"Filtered lines have been written to {output_file}")

    except FileNotFoundError:
        print(f"The file {input_file} does not exist.")
    except Exception as e:
        print(f"An error occurred: {e}")


# Usage
input_file = "hotels.txt"  # Replace with your input file name
output_file = "filtered-hotels.txt"
url = "/Hotels-Near-"

filter_lines_with_url(input_file, output_file, url)
