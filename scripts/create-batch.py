def split_file_by_content(
    input_file, output_prefix="output_file_", lines_per_file=1500
):
    """
    Splits a text file into multiple files, each with a maximum of 'lines_per_file' lines,
    writing the file contents to each output file.

    Args:
        input_file (str): Path to the input text file.
        output_prefix (str): Prefix for the output file names (e.g., "output_file_").
        lines_per_file (int): Maximum number of lines per output file.
    """
    try:
        with open(input_file, "r") as infile:
            file_number = 1
            line_count = 0
            output_file = None

            for line in infile:
                if line_count % lines_per_file == 0:
                    if output_file:  # Close the previous file
                        output_file.close()

                    output_filename = f"{output_prefix}{file_number}.txt"
                    output_file = open(output_filename, "w")
                    file_number += 1

                output_file.write(line)  # writes the actual content of the line.
                line_count += 1

            if output_file:  # Close the last file
                output_file.close()

        print(f"File '{input_file}' split successfully.")

    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")


# Example Usage:
input_file_path = "output-fv.txt"  # Replace with your input file
output_file_prefix = "batch_"  # Replace with your desired output file prefix.
lines_per_split_file = 1500  # Replace with the number of desired lines per file.


split_file_by_content(input_file_path, output_file_prefix, lines_per_split_file)
