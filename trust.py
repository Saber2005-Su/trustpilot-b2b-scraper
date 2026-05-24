import asyncio
import json
import csv
from playwright.async_api import async_playwright

async def scrape():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36'
        )
        page = await context.new_page()
        
        all_businesses = []
        
        for page_num in range(2, 6):  # Page 2 থেকে শুরু করছি (যেহেতু page 2 আগে কাজ করেছিল)
            print(f"\nScraping Page {page_num}...")
            
            url = f"https://www.trustpilot.com/_next/data/categoriespages-consumersite-2.1241.0/categories/business_services.json?page={page_num}&categoryId=business_services"
            
            try:
                await page.goto(url, wait_until='networkidle')
                await page.wait_for_timeout(2000)
                
                content = await page.inner_text('pre')
                data = json.loads(content)
                
                # Check if 'businessUnits' exists
                if 'pageProps' in data and 'businessUnits' in data['pageProps']:
                    businesses = data['pageProps']['businessUnits'].get('businesses', [])
                    
                    if not businesses:
                        print(f"Page {page_num}: No businesses found")
                        continue
                    
                    print(f"Page {page_num}: Found {len(businesses)} businesses")
                    
                    for business in businesses:
                        name = business.get('displayName', 'N/A')
                        phone = business.get('contact', {}).get('phone', 'N/A')
                        email = business.get('contact', {}).get('email', 'N/A')
                        
                        print(f"{name} | {phone} | {email}")
                        
                        all_businesses.append([name, phone, email])
                else:
                    print(f"Page {page_num}: businessUnits key not found in response")
                    # Print available keys for debugging
                    print(f"Available keys: {data.keys()}")
                    
            except Exception as e:
                print(f"Error scraping page {page_num}: {str(e)}")
                continue
        
        # CSV তে সেভ করা
        if all_businesses:
            csv_filename = 'business_data.csv'
            with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Name', 'Phone', 'Email'])  # Header
                writer.writerows(all_businesses)
            
            print(f"\n✓ Total {len(all_businesses)} businesses saved to {csv_filename}")
        else:
            print("\nNo data was scraped successfully!")
        
        await browser.close()

asyncio.run(scrape())