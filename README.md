# Scrapping Journal Database

## How to
1. Clone this repo by typing `git clone https://github.com/MaxKusnadi/is4241-webscrapper.git` in your terminal. Go to the directory `cd is4241-webscrapper`
2. Using Python 3 and `pip`, install all dependencies by typing `pip install -r requirements.txt` in your root folder
3. Install **Selenium** [here](https://sites.google.com/a/chromium.org/chromedriver/downloads). Unzip it and *move it to the root folder*
4. Ensure your Chrome is version > *64.x.x*. [How to check](https://www.howtogeek.com/299243/which-version-of-chrome-do-i-have/)
5. Open `run.py`. Put your **NUS ID** and **NUS PASSWORD** in `NUS_ID` and `NUS_PASSWORD` accordingly.
6. Adjust `START_INDEX` and `CHROME_PATH` if needed
7. Can change `LENGTH` to 2 or 3 first for testing
8. Run `python run.py`
9. Wait for 1-2 hours
10. Respective results in `result_2016.csv` and `result_all.csv`
