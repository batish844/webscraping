import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent

def setup_driver():
    options = Options()
    # Uncomment the headless option if you do not need a browser window.
    options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")
    
    # Use a random user-agent
    ua = UserAgent()
    options.add_argument(f"user-agent={ua.random}")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def scrape_coingecko_page():
    driver = setup_driver()
    url = "https://www.coingecko.com/"
    driver.get(url)
    # Wait for the table body element to be present
    table_xpath = "//tbody[@data-view-component='true']"
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, table_xpath))
        )
    except Exception as e:
        print("Error: Coin table did not load properly.")
        driver.quit()
        return []
    
    # Give extra time for dynamic content to load
    time.sleep(3)
    
    # Locate rows using a dynamic XPath (using contains() to be flexible with class names)
    row_xpath = "//tr[contains(@class, 'tw-text-sm') and contains(@class, 'hover:tw-bg-gray-50')]"
    rows = driver.find_elements(By.XPATH, row_xpath)
    
    coins = []
    for row in rows:
        try:
            # Image: locate by img element containing part of its class name
            image = row.find_element(By.XPATH, ".//img[contains(@class, 'tw-mr-2')]").get_attribute("src")
        except Exception:
            image = None
        
        try:
            # Coin name: get the element that holds the coin name
            name_element = row.find_element(By.XPATH, ".//div[contains(@class, 'tw-font-semibold') and contains(@class, 'tw-text-sm') and contains(@class, 'tw-leading-5')]")
            # Get only the direct text content (first text node) of the element
            coin_name = name_element.text.strip().split('\n')[0]
        except Exception:
            coin_name = None
        
        try:
            # Ticker: located in a nested element (using a class that contains 'tw-text-xs' and 'tw-leading-4')
            ticker_element = row.find_element(By.XPATH, ".//div[contains(@class, 'tw-text-xs') and contains(@class, 'tw-leading-4')]")
            coin_ticker = ticker_element.text.strip()
        except Exception:
            coin_ticker = None
        
        try:
            # Price: locate span with both data-price-target="price" and data-coin-id attributes
            price_element = row.find_element(By.XPATH, ".//span[@data-price-target='price' and @data-coin-id]")
            coin_price = price_element.text.strip()
        except Exception:
            coin_price = None
        
        try:
            # Price change 1h: using a dynamic attribute selector for data-attr
            price_change_1h = row.find_element(By.XPATH, ".//span[contains(@data-attr, 'price_change_percentage_1h')]").text.strip()
        except Exception:
            price_change_1h = None
        
        try:
            # Price change 24h
            price_change_24h = row.find_element(By.XPATH, ".//span[contains(@data-attr, 'price_change_percentage_24h')]").text.strip()
        except Exception:
            price_change_24h = None
        
        try:
            # Price change 7d
            price_change_7d = row.find_element(By.XPATH, ".//span[contains(@data-attr, 'price_change_percentage_7d')]").text.strip()
        except Exception:
            price_change_7d = None
        
        try:
            # Volume 24h and Market Cap: locate the td elements that contain the data
            volume_td_xpath = ".//td[.//span[@data-price-target='price' and not(@data-coin-id)] and contains(@data-sort, '')]"
            volume_tds = row.find_elements(By.XPATH, volume_td_xpath)
            
            if len(volume_tds) >= 2:
                sorted_tds = sorted(volume_tds, key=lambda td: float(td.get_attribute("data-sort") or 0))
                volume_24h = sorted_tds[0].find_element(By.XPATH, ".//span").text.strip()
                market_cap = sorted_tds[1].find_element(By.XPATH, ".//span").text.strip()
            else:
                volume_24h = None
                market_cap = None
        except Exception:
            volume_24h = None
            market_cap = None
        
        coins.append({
            "Image": image,
            "Name": coin_name,
            "Ticker": coin_ticker,
            "Price": coin_price,
            "Price Change 1h": price_change_1h,
            "Price Change 24h": price_change_24h,
            "Price Change 7d": price_change_7d,
            "24h Volume": volume_24h,
            "Market Cap": market_cap
        })
    
    driver.quit()
    return coins

def save_csv(data):
    file_name = "coingecko_scraped_data.csv"
    # Define the expected columns for consistency
    columns = ["Image", "Name", "Ticker", "Price", "Price Change 1h", 
               "Price Change 24h", "Price Change 7d", "24h Volume", "Market Cap"]
    try:
        df = pd.read_csv(file_name)
    except FileNotFoundError:
        df = pd.DataFrame(columns=columns)
    
    # Create a DataFrame from new data
    new_df = pd.DataFrame(data)
    df = pd.concat([df, new_df], ignore_index=True)
    df.to_csv(file_name, index=False)
    print("Data saved to CSV file.")

def main():
    coins_data = scrape_coingecko_page()
    if coins_data:
        # You can print the new data or the whole DataFrame if desired
        df_new = pd.DataFrame(coins_data)
        print(df_new)
        save_csv(coins_data)
    else:
        print("No data scraped.")

if __name__ == '__main__':
    main()
