
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from test.utils import fetch_article_links, filter_and_scrape_articles, save_results_to_csv, load_urls_from_csv

# Define today as a global variable
today = datetime.today().date()

def main():
    # Start measuring time
    start_time = time.time()
    
    # Load URLs from a CSV file
    csv_filename = 'site_urls.csv'  # Update with your actual CSV filename
    sites = load_urls_from_csv(csv_filename)
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    all_article_links = []

    # Use ThreadPoolExecutor to fetch articles concurrently
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_site = {}
        for site in sites:
            future = executor.submit(
                fetch_article_links, 
                site['page_url'], 
                headers, 
                today, 
                site['navigation_type']
            )
            future_to_site[future] = site

        for future in as_completed(future_to_site):
            site = future_to_site[future]
            try:
                article_links = future.result()
                all_article_links.extend(article_links)
                time.sleep(5)  # Delay between requests to avoid overloading the server
            except Exception as e:
                print(f"Error processing site {site['page_url']}: {e}")
    
    print("Filtering articles published today and scraping content...")
    results = filter_and_scrape_articles(all_article_links, today)
    
    # Generate the output filename with the current date
    today_date_str = today.strftime('%d-%m-%Y')
    output_csv_file = f'scraped_article_{today_date_str}.csv'
    
    # Save results to CSV file
    save_results_to_csv(results, output_csv_file)
    
    print(f"Results saved to {output_csv_file}")
    
    # Stop measuring time and print the elapsed time
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Execution time: {elapsed_time:.2f} seconds")

if __name__ == "__main__":
    main()
