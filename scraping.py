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
from datetime import datetime

options = Options()
    # Uncomment the headless option if you do not need a browser window.
options.add_argument("--headless")
options.add_argument("--window-size=1920,1080")
    
    # Use a random user-agent
ua = UserAgent()
options.add_argument(f"user-agent={ua.random}")
    
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)
def scrape_data(url):
    driver.get(url)
    time.sleep(5)
    try:
        price = WebDriverWait(driver,15).until(
            EC.presence_of_element_located((By.XPATH, '//span[@data-test="text-cdp-price-display"]'))
        ).text
        market_cap = WebDriverWait(driver,15).until(
            EC.presence_of_element_located((By.XPATH,"//dt[.//div[contains(text(),'Market cap')]]/following-sibling::dd//span")
        )).text
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        bitcoin_data = {
            "timestamp": timestamp,
            "price": price,
            "market_cap": market_cap
        }
        return bitcoin_data
    
    except Exception as e:
        print("Error: ",e)
        return None
    
def save_csv(data):
    file_name = "bitcoin_min_data.csv"
    try:
        df = pd.read_csv(file_name)
    except FileNotFoundError:
        df = pd.DataFrame(columns=["timestamp","price","market_cap"])
    
    new_row = pd.DataFrame([data])
    df = pd.concat([df,new_row],ignore_index=True)
    df.to_csv(file_name,index=False)

if __name__=="__main__":
    url = "https://coinmarketcap.com/currencies/bitcoin/"

    print("Scraping data...")
    data = scrape_data(url)
    if data:
        save_csv(data)
        print("Data scraped...")
    else:
        print("No data")

    driver.quit()