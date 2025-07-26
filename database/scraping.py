import json
import time
import re
from urllib.parse import quote_plus

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

import json
import time
import re
from urllib.parse import quote_plus
import undetected_chromedriver as uc
from bs4 import BeautifulSoup

def get_first_search_result(driver, boss_name):
    """
    Uses an undetected chromedriver to search Fextralife and return the URL of the first result.
    """
    base_url = "https://eldenring.wiki.fextralife.com/Elden+Ring+Wiki"
    
    # Clean up the name for a better search query
    search_term = re.sub(r'\(.+\)', '', boss_name).strip()
    search_term = search_term.split('&')[0].strip()

    query = quote_plus(search_term)
    search_url = f"{base_url}#gsc.tab=0&gsc.q={query}&gsc.sort="
    
    try:
        driver.get(search_url)
        # Give the page a generous amount of time to load, including handling any pop-ups
        time.sleep(5) # Increased sleep to allow for CMP and JS loading

        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        
        # The selector for the first search result link
        first_result = soup.select_one('div.gs-webResult a.gs-title')
        
        if first_result and first_result.has_attr('href'):
            link = first_result['href']
            if not link.startswith("http"):
                 return "https://eldenring.wiki.fextralife.com" + link
            return link
        else:
            # If the primary selector fails, it might be because the page didn't load correctly.
            # We can look for any link to the wiki as a fallback.
            fallback_result = soup.find('a', href=re.compile(r'fextralife.com/' + re.escape(search_term.replace(" ", "+")), re.IGNORECASE))
            if fallback_result:
                return fallback_result['href']
            return "NOT_FOUND"
            
    except Exception as e:
        print(f"  An error occurred for '{boss_name}': {e}")
        return "ERROR"

def main():
    # --- Setup Selenium WebDriver ---
    print("Setting up browser driver...")
    options = uc.ChromeOptions()
    # Run with a visible window first to debug any issues.
    # Once confirmed working, you can uncomment the headless line.
    # options.add_argument('--headless=new') 
    driver = uc.Chrome(options=options)
    print("Driver setup complete.")

    # --- "Warm Up" Phase ---
    main_page_url = "https://eldenring.wiki.fextralife.com/"
    print(f"Navigating to main page to handle cookies/consent: {main_page_url}")
    driver.get(main_page_url)
    # Give it a generous pause to let the cookie banner be handled.
    # You can observe this visually when not in headless mode.
    print("Pausing for 10 seconds to allow for page setup...")
    time.sleep(10)
    print("Warm-up complete. Starting search process.")

    # --- Load your boss data ---
    try:
        with open('database/boss_datav2.json', 'r', encoding='utf-8') as f:
            boss_list = json.load(f)
    except FileNotFoundError:
        print("Error: 'boss_data_processed.json' not found. Please run your processing script first.")
        driver.quit()
        return

    # --- Scrape for each boss ---
    for i, boss in enumerate(boss_list):
        # Skip if link already exists (allows resuming a failed run)
        if 'link' in boss and boss['link'] not in ["NOT_FOUND", "ERROR"]:
            continue

        print(f"Processing ({i+1}/{len(boss_list)}): {boss['name']}...")
        
        link = get_first_search_result(driver, boss['name'])
        boss['link'] = link
        
        print(f"  -> Found: {link}")
        
        # Be polite! Wait 1-2 seconds between requests.
        time.sleep(1.5) 

    # --- Cleanup and Save ---
    driver.quit()
    
    with open('util/boss_data_with_links.json', 'w', encoding='utf-8') as f:
        json.dump(boss_list, f, indent=2)
        
    print("\nProcessing complete!")
    print("Enriched data saved to 'boss_data_with_links.json'")


if __name__ == "__main__":
    main()