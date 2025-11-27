from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from datetime import datetime, date
import pandas as pd
from sqlalchemy import create_engine
import os
import time
import random
import psycopg2
import keyring
import getpass
from dotenv import load_dotenv


def scrapehtml(html: str):
    soup = BeautifulSoup(html, "html.parser")
    target_divs = soup.find_all("div", class_="bc-side-widget-content")

    div_data = []
    for div in target_divs:
        if "Date" in div.get_text():
                        
            tables = div.find_all("table")
            if tables:
                rows = tables[0].find_all("tr")
                
                for row in rows:                    
                    tds = row.find_all("td")                    
                    if tds:
                        div_date_raw = tds[0].get_text(strip=True)
                        div_date = datetime.strptime(div_date_raw, "%m/%d/%y").date()  # YYYY-MM-DD format
                        div_value = tds[1].get_text(strip=True).replace("$", "")
                        div_data.append((div_date, div_value))
                                                  
    return div_data

def main():

    def getbrowserpage(p):        
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        return browser, page, 0

    all_div_data = []       
    page_maxreads = 4
    # tickers = ['ABCL','ASEA','ATD.TO','BTO.TO','CHRD','CS.TO','CTRA','CVE.TO','CRMD','DRM.TO','ENB.TO','ET','FILL','FLGT','FLIN','FURCF','GPN','HAI.TO','ILLM.TO','NEO.TO','NEXA','NOA.TO','NPI.TO','NSCI.TO','NTR.TO','NVDA','PERI','PPLN.TO','PRG','PSD.TO','QTRH.TO','RBY.TO','REAL.TO','SGR.UN.TO','SHEL','SID','SOBO.TO','T.TO','TRP.TO','TTE','VALE','VET.TO','WCP.TO','XEG.TO']
    tickers = ['ABCL','ASEA','ATD.TO','BTO.TO','CHRD','CS.TO','CTRA','CVE.TO','CRMD','DRM.TO','ENB.TO','ET','FILL','FLGT','FLIN','FURCF','GPN','HAI.TO','ILLM.TO','NEO.TO','NEXA','NOA.TO','NPI.TO']
    watch_2025_09 = ['AMRK','AMZN','META','MU','BBW','MSFT','NVDA','NVT','PLAB','POWL','SLSR','TSM','APOG','AZZ','CEG','GOOGL','MRX','OI','OPRA','PLTR','SBH','SCSC','TPG']
    tickers.extend(watch_2025_09)
    tickers.reverse()
        
    with sync_playwright() as p:

        browser, page, page_reads = getbrowserpage(p)
        
        while tickers:
            ticker = tickers.pop()
            page_reads += 1
            if  page_reads > page_maxreads:
                browser.close()
                browser, page, page_reads = getbrowserpage(p)      
                
            
            url = f"https://www.barchart.com/stocks/quotes/{ticker}/profile"
            print(f"Processing {ticker}...")        
            
            page.goto(url, wait_until="domcontentloaded")   #parse the DOM quickly
            page.wait_for_selector("div.bc-side-widget-content", state="visible")   # wait for the right widget to load
            print(page.title())
            pagehtml = page.content()

            div_data = scrapehtml(pagehtml)
            div_data = [(ticker, d[0], d[1]) for d in div_data]
            print("div_data:", div_data)  
            all_div_data.extend(div_data)
            
            time.sleep(random.uniform(0, 5))            
            
        page.close()
        browser.close()
    print('exiting')

    
    if all_div_data:
        # Save to database        
        df = pd.DataFrame(all_div_data, columns=["ticker", "div_exdiv_date", "div_amt"])
        df.insert(0, 'sample_date', date.today())        
        df.insert(2, 'company_name', '')
        print(df.head())

        load_dotenv()
        _db_user = os.getenv('DBUSER')        
        _db_pw = keyring.get_password(os.getenv("KEYRING_SERVICE"), os.getenv("KEYRING_USER"))
        _host = os.getenv('HOST')
        _port = os.getenv('PORT')
        _database = os.getenv('DATABASE')
        
        engine = create_engine(f"postgresql+psycopg2://{_db_user}:{_db_pw}@{_host}:{_port}/{_database}")

        df.to_sql('div_hist_bc', con=engine, if_exists='append', index=False, method='multi')
        print(f"Saved {len(all_div_data)} records to database.")
    
        # df = pd.read_sql("SELECT * FROM stock limit 5", engine)
        # print(df)



if __name__ == "__main__":
    main()