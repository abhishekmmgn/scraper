import xml.etree.ElementTree as ET
import requests


# Function to fetch and parse sitemap URLs
def fetch_sitemap_urls(sitemap_url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    try:
        response = requests.get(sitemap_url, headers=headers)
        response.raise_for_status()  # Check for HTTP errors
        sitemap_content = response.content
    except requests.RequestException as e:
        print(f"Error fetching sitemap {sitemap_url}: {e}")
        return []

    try:
        sitemap_tree = ET.ElementTree(ET.fromstring(sitemap_content))
        sitemap_root = sitemap_tree.getroot()
    except ET.ParseError as e:
        print(f"Error parsing sitemap {sitemap_url}: {e}")
        return []

    namespace = {"ns": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    urls = [
        url.find("ns:loc", namespace).text
        for url in sitemap_root.findall("ns:url", namespace)
    ]
    return urls


# Read sitemap URLs from a text file
input_file = "sitemap_urls.txt"
output_file = "extracted_urls.txt"

try:
    with open(input_file, "r") as file:
        sitemap_urls = [line.strip() for line in file.readlines()]
except FileNotFoundError:
    print(f"Error: The file {input_file} does not exist.")
    exit(1)

# List to hold all extracted URLs
all_extracted_urls = []

# Fetch and parse each sitemap URL
for sitemap_url in sitemap_urls:
    extracted_urls = fetch_sitemap_urls(sitemap_url)
    all_extracted_urls.extend(extracted_urls)

# Export the extracted URLs to a file
with open(output_file, "w") as file:
    for url in all_extracted_urls:
        file.write(url + "\n")

print(f"URLs have been successfully exported to {output_file}")
