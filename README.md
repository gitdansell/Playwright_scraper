# Playwright Scraper

Firstly, Playwright Scraper is an exploratory project to begin using Playwright and move away from Selenium for the purpose of scraping webdata.

simple_sync.py is the first file to have real functionality. The other .py files are experimentation and have limited purpose.

**Features of simple_sync.py include:**
* Synchronous Playwright (as opposed to async)
* BeautifulSoup for html parsing
* Uses a **.env** file for safeguarding meta data
* Uses **keyring** for safeguarding passwords
* Uses Pandas and SQLAlchemy for persisting records into a database

## Installation

Edit your own .env file with configuration details:
```bash
cp .env_dummy_ .env      # macOS/Linux
copy .env_dummy .env    # Windows
```

Use the **uv** package manager to install dependencies and run simple_sync.py:

```bash
# if uv is not already installed
sudo pip3 install uv    # macOS/Linux
pip install uv          # Windows (Administrator Command Prompt)

uv sync
uv run simple_sync.py
```