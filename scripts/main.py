import xml.etree.ElementTree as ET
import requests

# Parse the sitemap index file
index_tree = ET.parse("sitemap_index.xml")
index_root = index_tree.getroot()

# Define the namespace
namespace = {"ns": "http://www.sitemaps.org/schemas/sitemap/0.9"}

# List to hold all URLs
all_urls = []

# Headers to mimic a browser request
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}

# Iterate through each sitemap in the index
for sitemap in index_root.findall("ns:sitemap", namespace):
    sitemap_url = sitemap.find("ns:loc", namespace).text
    try:
        response = requests.get(sitemap_url, headers=headers)
        response.raise_for_status()  # Check for HTTP errors
        sitemap_tree = ET.ElementTree(ET.fromstring(response.content))
        sitemap_root = sitemap_tree.getroot()

        # Extract URLs from the current sitemap
        urls = [
            url.find("ns:loc", namespace).text
            for url in sitemap_root.findall("ns:url", namespace)
        ]
        all_urls.extend(urls)
    except requests.RequestException as e:
        print(f"Error fetching sitemap {sitemap_url}: {e}")
    except ET.ParseError as e:
        print(f"Error parsing sitemap {sitemap_url}: {e}")

# Print all URLs
for url in all_urls:
    print(url)
