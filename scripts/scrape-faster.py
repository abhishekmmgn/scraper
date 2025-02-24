import aiohttp
import asyncio
import csv
import random
import time
from aiohttp import ClientSession
from bs4 import BeautifulSoup
from async_timeout import timeout

# User-Agent rotation
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
]

# Semaphore to control concurrency (100 requests at a time)
semaphore = asyncio.Semaphore(100)


# Randomized delay to prevent rate-limiting
def random_sleep():
    return random.uniform(2, 5)  # Sleep for 2-5 seconds between requests


# Function to get random headers
def get_random_headers():
    return {"User-Agent": random.choice(USER_AGENTS)}


# Asynchronous scraping function with retries and exponential backoff
async def scrape_hotel_data(url, session):
    async with semaphore:  # Limit concurrent requests
        for attempt in range(3):  # Retry up to 3 times
            try:
                async with timeout(15):  # Set timeout for request
                    async with session.get(
                        url, headers=get_random_headers()
                    ) as response:
                        if response.status == 200:
                            soup = BeautifulSoup(await response.text(), "html.parser")

                            # Extract hotel details
                            def safe_extract(selector, attr=None):
                                element = soup.select_one(selector)
                                if element:
                                    return (
                                        element[attr] if attr else element.text.strip()
                                    )
                                return "N/A"

                            hotel_name = safe_extract("h1.title-xxl")
                            address = safe_extract("p.hotel-address")
                            phone = safe_extract("p.hotel-phone-number strong")
                            fax = safe_extract("p.hotel-fax-number strong")
                            hotel_email = safe_extract(
                                "p.hotel-email a", "href"
                            ).replace("mailto:", "")
                            hotel_website = safe_extract("p.hotel-website a", "href")
                            hotel_classification = safe_extract("p.hotel-rating")
                            commission = safe_extract("p.hotel-commission strong")
                            rooms = safe_extract("p.hotel-rooms strong")
                            rates = safe_extract("p.hotel-rates strong")
                            overview_text = safe_extract(
                                "div.hotel-overview p:nth-of-type(2)"
                            )

                            # Extract additional details
                            details_div = soup.select_one(
                                "div.hotel-information-details:has(h4:contains('Details'))"
                            )

                            year_built = "N/A"
                            year_last_renovated = "N/A"
                            chain = "N/A"
                            chain_website = "N/A"

                            if details_div:
                                for p in details_div.find_all("p"):
                                    text = p.get_text(strip=True)
                                    if "Year Built:" in text:
                                        year_built = (
                                            p.find("strong").text.strip()
                                            if p.find("strong")
                                            else "N/A"
                                        )
                                    if "Year Last Renovated:" in text:
                                        year_last_renovated = (
                                            p.find("strong").text.strip()
                                            if p.find("strong")
                                            else "N/A"
                                        )
                                    if "Chain:" in text:
                                        chain = (
                                            p.find("a").text.strip()
                                            if p.find("a")
                                            else "N/A"
                                        )
                                    if "Chain Website" in text:
                                        chain_website = (
                                            p.find("a")["href"]
                                            if p.find("a")
                                            else "N/A"
                                        )

                            # Extract discounts
                            discounts = ", ".join(
                                p.text.strip()
                                for p in soup.select(
                                    "div.hotel-information-details h4:contains('Discounts offered') + div p"
                                )
                            )

                            # Extract images
                            image_urls = ", ".join(
                                img["src"]
                                for img in soup.select(
                                    "div.photo-gallery img.img-responsive"
                                )
                            )

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
                print(f"Attempt {attempt + 1} failed for {url}: {e}")
                await asyncio.sleep(2**attempt)  # Exponential backoff

        print(f"Failed to scrape: {url}")
        return [url] + ["ERROR"] * 16  # Return error placeholders


# Asynchronous main function
async def main():
    input_file = "urls.txt"  # File containing URLs
    output_file = "hotel_data.csv"

    # Read URLs from file
    with open(input_file, "r") as file:
        urls = [line.strip() for line in file.readlines() if line.strip()]

    csv_headers = [
        "URL",
        "Hotel Name",
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
        "Discounts Offered",
        "Image URLs",
    ]

    async with aiohttp.ClientSession() as session:
        # Scrape all URLs asynchronously
        results = await asyncio.gather(
            *[scrape_hotel_data(url, session) for url in urls]
        )

        # Save results to CSV
        with open(output_file, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(csv_headers)
            writer.writerows(results)

    print(f"Scraping completed! Data saved to {output_file}")


# Run the async event loop
if __name__ == "__main__":
    asyncio.run(main())
