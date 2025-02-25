import aiohttp
import requests
import asyncio
import csv
import random
from bs4 import BeautifulSoup
from aiohttp import ClientTimeout, TCPConnector
from tenacity import retry, stop_after_attempt, wait_exponential
import time

# List of User Agents (rotating to avoid blocks)
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
]

# List of free proxies (replace with a proxy pool for better results)
PROXIES = [
    "http://8.8.8.8:8080",
    "http://1.1.1.1:3128",
]


# Function to get random headers
def get_random_headers():
    return {"User-Agent": random.choice(USER_AGENTS)}


# Function to get a random proxy
def get_random_proxy():
    return random.choice(PROXIES)


# Log failed URLs for retry
def log_failed_url(url):
    with open("errors.txt", "a") as f:
        f.write(url + "\n")


# Exponential backoff for retrying failed requests
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, min=2, max=8))
async def fetch(session, url):
    proxy = get_random_proxy()
    try:
        async with session.get(
            url,
            headers=get_random_headers(),
            proxy=proxy,
            timeout=ClientTimeout(total=10),
        ) as response:
            response.raise_for_status()
            return await response.text()
    except Exception as e:
        print(f"Primary request failed for {url}, trying Google Cache... Error: {e}")
        return await fetch_google_cache(session, url)


# Function to fetch Google Cache fallback
async def fetch_google_cache(session, url):
    cache_url = (
        f"https://webcache.googleusercontent.com/search?q=cache:{url}&strip=1&vwsrc=1"
    )
    try:
        async with session.get(
            cache_url, headers=get_random_headers(), timeout=ClientTimeout(total=10)
        ) as response:
            response.raise_for_status()
            return await response.text()
    except Exception as e:
        print(f"Google Cache failed for {url}: {e}")
        log_failed_url(url)
        return None


# Asynchronous scraping function
async def scrape_hotels(urls, output_file):
    tasks = []
    connector = TCPConnector(limit=50)  # Concurrency limited to 50
    async with aiohttp.ClientSession(connector=connector) as session:
        for url in urls:
            tasks.append(fetch(session, url))

        responses = await asyncio.gather(*tasks)

        with open(output_file, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
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

            for url, html in zip(urls, responses):
                if html:
                    data = scrape_hotel_data(html, url)
                    writer.writerow(data)
                else:
                    log_failed_url(url)
    print("Scraping completed! Data saved.")


# Main function to run the async scraper
def main():
    input_file = "batches/batch_1.txt"
    output_file = "hotel_data.csv"

    with open(input_file, "r") as file:
        urls = [line.strip() for line in file.readlines() if line.strip()]

    print(f"Scraping {len(urls)} URLs...")
    start_time = time.time()

    asyncio.run(scrape_hotels(urls, output_file))

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Scraping completed in {elapsed_time:.2f} seconds.")


if __name__ == "__main__":
    main()
