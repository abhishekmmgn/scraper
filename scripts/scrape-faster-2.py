import csv
from bs4 import BeautifulSoup
import aiohttp
import asyncio
import time
import os
import requests
import concurrent.futures

SCRAPER_API_KEY = "1be97fc0462e779b692f969205135cd5"
NUM_RETRIES = 3
NUM_THREADS = 5
INPUT_FILE = "batches/2.txt"
OUTPUT_FILE = "output-1.csv"


# Log failed URLs for retry
def log_failed_url(url):
    with open("errors.txt", "a") as f:
        f.write(url + "\n")


def fetch(url):
    """Fetch the webpage content from ScraperAPI."""
    payload = {"api_key": SCRAPER_API_KEY, "url": url}
    # timeout = aiohttp.ClientTimeout(total=70)

    for x in range(NUM_RETRIES):
        try:
            response = requests.get("http://api.scraperapi.com/", params=payload)
            if response.status_code == 200:
                return response.text
            else:
                print(
                    f"{x + 1} request failed for {url} with status code {response.status_code}"
                )
        except requests.exceptions.ClientError as e:
            print(f"{x + 1} request failed for {url} with ClientError: {e}")
        except Exception as e:
            print(f"{x + 1} request failed for {url} --> {e}")

    print(f"\nAll retries failed for {url}\n")
    return None


def scrape_hotel_data(html, url):
    if not html:  # Check if the response is None
        print(f"Error: No HTML received for {url}")
        log_failed_url(url)
        return None

    try:
        soup = BeautifulSoup(html, "html.parser")

        # Extract relevant data
        hotel_name = (
            soup.find("h1", class_="title-xxl").text.strip()
            if soup.find("h1", class_="title-xxl")
            else "N/A"
        )
        address = (
            soup.find("p", class_="hotel-address").text.strip()
            if soup.find("p", class_="hotel-address")
            else "N/A"
        )
        phone = (
            soup.select_one("p.hotel-phone-number strong").text.strip()
            if soup.select_one("p.hotel-phone-number strong")
            else "N/A"
        )
        fax = (
            soup.select_one("p.hotel-fax-number strong").text.strip()
            if soup.select_one("p.hotel-fax-number strong")
            else "N/A"
        )
        hotel_email = (
            soup.find("p", class_="hotel-email")
            .find("a")["href"]
            .replace("mailto:", "")
            if soup.find("p", class_="hotel-email")
            and soup.find("p", class_="hotel-email").find("a")
            else "N/A"
        )
        hotel_website = (
            soup.find("p", class_="hotel-website").find("a")["href"]
            if soup.find("p", class_="hotel-website")
            else "N/A"
        )
        hotel_classification = (
            soup.find("p", class_="hotel-rating").text.strip()
            if soup.find("p", class_="hotel-rating")
            else "N/A"
        )
        commission = (
            soup.select_one("p.hotel-commission strong").text.strip()
            if soup.select_one("p.hotel-commission strong")
            else "N/A"
        )
        rooms = (
            soup.select_one("p.hotel-rooms strong").text.strip()
            if soup.select_one("p.hotel-rooms strong")
            else "N/A"
        )
        rates = (
            soup.select_one("p.hotel-rates strong").text.strip()
            if soup.select_one("p.hotel-rates strong")
            else "N/A"
        )
        overview_text = (
            soup.select_one("div.hotel-overview p:nth-of-type(2)").text.strip()
            if soup.select_one("div.hotel-overview p:nth-of-type(2)")
            else "N/A"
        )

        # Extract details section
        details_div = next(
            (
                div
                for div in soup.find_all("div", class_="hotel-information-details")
                if div.find("h4") and "Details" in div.find("h4").text
            ),
            None,
        )

        year_built = "N/A"
        if details_div:
            for p in details_div.find_all("p"):
                if "Year Built:" in p.get_text():
                    strong_tag = p.find("strong")
                    if strong_tag:
                        year_built = strong_tag.get_text(strip=True)
                    break

        year_last_renovated = "N/A"
        if details_div:
            for p in details_div.find_all("p"):
                if "Year Last Renovated:" in p.get_text():
                    strong_tag = p.find("strong")
                    if strong_tag:
                        year_last_renovated = strong_tag.get_text(strip=True)
                    break

        chain = "N/A"
        if details_div:
            for p in details_div.find_all("p"):
                if "Chain:" in p.get_text():
                    a_tag = p.find("a")
                    if a_tag:
                        chain = a_tag.get_text(strip=True)
                    break

        chain_website = "N/A"
        if details_div:
            for a_tag in details_div.find_all("a", href=True):
                if "Chain Website" in a_tag.get_text(strip=True):
                    chain_website = a_tag["href"]
                    break

        # Extract discounts
        discounts_div = next(
            (
                div
                for div in soup.find_all("div", class_="hotel-information-details")
                if div.find("h4") and "Discounts offered" in div.find("h4").text
            ),
            None,
        )

        discounts = (
            ", ".join(p.text.strip() for p in discounts_div.find_all("p"))
            if discounts_div
            else "N/A"
        )

        # Extract image URLs
        image_urls_list = [
            img["src"] for img in soup.select("div.photo-gallery img.img-responsive")
        ]
        image_urls = ", ".join(image_urls_list)

        return [
            url,
            hotel_name,
            address,
            phone,
            fax,
            hotel_email,
            hotel_website,
            hotel_classification,
            commission,
            rooms,
            rates,
            overview_text,
            year_built,
            year_last_renovated,
            chain,
            chain_website,
            discounts,
            image_urls,
        ]

    except Exception as e:
        print(f"Error parsing {url}: {e}")
        log_failed_url(url)
        return None


def scrape_hotels(url):
    """Fetch and extract hotel data for a given URL."""
    html = fetch(url)
    if not html:
        return None

    return scrape_hotel_data(html, url)


def main():
    try:
        with open(INPUT_FILE, "r") as file:
            urls = [line.strip() for line in file.readlines() if line.strip()]

    except Exception as e:
        print(f"Scraping {len(urls)} URLs... {e}")

    if not urls:
        print("No URLs found in the input file.")
        return

    start_time = time.time()

    with open(OUTPUT_FILE, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        file_exists = os.path.isfile(OUTPUT_FILE)
        if not file_exists or os.stat(OUTPUT_FILE).st_size == 0:
            writer.writerow(
                [
                    "Link",
                    "Name",
                    "Address",
                    "Phone",
                    "Fax",
                    "Hotel Email",
                    "Hotel Website",
                    "Hotel Classification",
                    "Commission",
                    "Rooms",
                    "Rates",
                    "Overview Text",
                    "Year Built",
                    "Year Last Renovated",
                    "Chain",
                    "Chain Website",
                    "Discounts offered",
                    "Image URLs",
                ]
            )

        # ! --------------------------------- NEW --------------------------------------
        with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
            results = executor.map(scrape_hotels, urls)

            for url, data in zip(urls, results):
                if data is not None:
                    writer.writerow(data)
                else:
                    print(f"Failed to retrieve or parse data for {url}")

    end_time = time.time()

    print(f"Scraping completed in {end_time - start_time} seconds.")


# Run the script
if __name__ == "__main__":
    main()
