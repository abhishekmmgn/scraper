import requests
import time
import json

API_KEY = "4f30b785a3333016997762b6f7f314c4"  # Replace with your ScraperAPI key
URL = "https://www.travelweekly.com/Hotels/Yalova-Turkey/Crowne-Plaza-Yalova-p59791558"  # Target URL


# Step 1: Submit an async job
def submit_scraping_job(url):
    response = requests.post(
        url="https://async.scraperapi.com/jobs",
        json={
            "apiKey": API_KEY,
            "url": url,
        },
    )

    data = response.json()
    job_id = data.get("id")
    status_url = data.get("statusUrl")

    if job_id:
        print(f"✅ Job submitted successfully. Job ID: {job_id}")
        return status_url
    else:
        print(f"❌ Error submitting job: {data}")
        return None


# Step 2: Poll the job status until it’s finished
def wait_for_scraping_completion(status_url):
    while True:
        response = requests.get(status_url)
        data = response.json()

        status = data.get("status")
        if status == "finished":
            print("✅ Scraping job completed.")
            return data.get("response", {})
        elif status == "failed":
            print("❌ Scraping job failed.")
            return None
        else:
            print(f"⏳ Job still running... Status: {status}")
            time.sleep(5)  # Wait 5 seconds before checking again


# Step 3: Save results to a file
def save_results(results, filename="scraped_results.json"):
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(results, file, indent=4)
    print(f"📁 Results saved to {filename}")


# Run the scraping process
status_url = submit_scraping_job(URL)
if status_url:
    results = wait_for_scraping_completion(status_url)
    if results:
        save_results(results)
