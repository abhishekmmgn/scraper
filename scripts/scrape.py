import aiohttp
import requests
import asyncio
import csv
import random
from bs4 import BeautifulSoup
from aiohttp import ClientTimeout
from tenacity import retry, stop_after_attempt, wait_exponential

# List of User Agents (rotating to avoid blocks)
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
]

# List of free proxies (add more for better performance)
PROXIES = [
    "http://8.8.8.8:8080",
    "http://1.1.1.1:3128",
]


# Function to get random headers
def get_random_headers():
    return {"User-Agent": random.choice(USER_AGENTS)}


# Function to get a random proxy
def get_random_proxy():
    proxy = random.choice(PROXIES)
    return {"http": proxy, "https": proxy}


def scrape_with_fallback(url):
    try:
        response = requests.get(url, headers=get_random_headers(), timeout=10)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException:
        print(f"Using Google Cache for {url}")
        cache_url = f"https://webcache.googleusercontent.com/search?q=cache:{url}&strip=1&vwsrc=1"
        try:
            response = requests.get(cache_url, headers=get_random_headers(), timeout=10)
            response.raise_for_status()
            return response.content
        except:
            print(f"Failed to get cached version: {url}")
            return None  # Mark failure explicitly


# Exponential backoff for retrying failed requests
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def fetch(session, url):
    try:
        async with session.get(
            url, headers=get_random_headers(), timeout=ClientTimeout(total=10)
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
        return None  # Return None if both fail


def scrape_hotel_data(html, url):
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
        return [url] + ["ERROR"] * 7  # Return placeholders on failure


# Asynchronous scraping function
async def scrape_hotels(urls, output_file):
    tasks = []
    async with aiohttp.ClientSession() as session:
        for url in urls:
            tasks.append(fetch(session, url))

        responses = await asyncio.gather(*tasks)

        # Process responses
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


# Main function to run the async scraper
def main():
    input_file = "batches/batch_1.txt"
    output_file = "/output_csv/hotel_data_1.csv"

    # Read URLs from file
    with open(input_file, "r") as file:
        urls = [line.strip() for line in file.readlines() if line.strip()]

    print(f"Scraping {len(urls)} URLs...")

    # Run the async scraper
    asyncio.run(scrape_hotels(urls, output_file))

    print(f"Scraping completed! Data saved to {output_file}")


# Run the script
if __name__ == "__main__":
    main()
