from selenium import webdriver
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup

import time
import logging

NUS_ID = ""
NUS_PASSWORD = ""
ID_TYPE = "NUSSTU"
START_INDEX = 0
LENGTH = 300

CHROME_PATH = './chromedriver'
TOTAL_JOURNAL = 1493
LOGIN_LINK = "https://proxylogin.nus.edu.sg/libproxy1/public/login.asp?logup=false&url=https://jcr.incites.thomsonreuters.com"
JOURNAL_TEXT = "journals.txt"
CSV_ALL_RESULT = "result_all.csv"
CSV_2016_RESULT = "result_2016.csv"

class Scrapper:

    def __init__(self):
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.journals_dict, self.journals_list = self._get_journals()
        self.csv, self.csv_2016 = self._get_csv()
        self.driver = self._get_driver()
        self.soup = None

    def _get_journals(self):
        # Reading journals
        logging.info("Getting journal info")
        journals = dict()
        journal_list = []
        with open(JOURNAL_TEXT, 'r') as f:
            for line in f:
                journals[line.strip()] = 0
                journal_list.append(line.strip())
        return journals, journal_list

    def _get_csv(self):
        logging.info("Preparing CSV file")
        csv = open(CSV_ALL_RESULT, 'w')
        csv.write("Journal Name,")
        csv.write(",".join(self.journals_list))
        csv.write("\n")

        csv_2016 = open(CSV_2016_RESULT, 'w')
        csv_2016.write("Journal Name,")
        csv_2016.write(",".join(self.journals_list))
        csv_2016.write("\n")

        return csv, csv_2016

    def _get_driver(self):
        # Creating drive
        logging.info("Initializing the driver")
        driver = webdriver.Chrome(CHROME_PATH)
        driver.implicitly_wait(30)
        return driver

    def login(self):
        # Trying to login
        logging.info("Signing in to the system")
        self.driver.get(LOGIN_LINK)
        domain = Select(self.driver.find_element_by_name("domain"))
        domain.select_by_value(ID_TYPE)

        username = self.driver.find_element_by_name("user")
        password = self.driver.find_element_by_name("pass")
        username.send_keys(NUS_ID)
        password.send_keys(NUS_PASSWORD)

        self.driver.find_element_by_xpath("//input[@value='Login']").click()
        self.driver.find_element_by_xpath("//input[@value='I Accept']").click()
        logging.info("Login successful")

    def select_journal(self, journal):
        # Selecting journals
        logging.info("Get journal info of {}".format(journal))
        is_clicked = False
        while not is_clicked:
            try:
                logging.info("Trying to click the sidebar...")
                self.driver.find_element_by_class_name("checkbox-journals").click()
            except:
                pass
            else:
                is_clicked = True

        logging.info("Typing the journal name in the search bar")
        journal_search = self.driver.find_element_by_name("journalSearch-inputEl")
        journal_search.send_keys(journal)
        succeed = False
        journal_name = None
        while not succeed:
            try:
                logging.info("Clicking on the dropdown options...")
                _journal = self.driver.find_element_by_class_name("x-boundlist-item")
                journal_name = _journal.text
                _journal.click()
            except:
                logging.error("Dropdown clicking failed")
                journal_search.clear()
                journal_search.send_keys(journal)
            else:
                succeed = True
        logging.info("Clicking {}".format(journal_name))
        is_submitted = False
        while not is_submitted:
            try:
                self.driver.find_element_by_link_text('Submit').click()
                self.driver.find_element_by_link_text('Select All')
            except:
                pass
            else:
                is_submitted = True

        is_clicked = False
        while not is_clicked:
            try:
                logging.info("Clicking the journal on the main body")
                self.driver.find_element_by_xpath('//a[contains(translate(., "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "{}")]'.format(journal_name.lower())).click()
            except:
                logging.error("Clicking failed...")
                pass
            else:
                is_clicked = True

        is_citing_journal_clicked = False
        while not is_citing_journal_clicked:
            try:
                self.driver.find_element_by_link_text("Citing Journal Data").click()
            except:
                pass
            else:
                try:
                    test = self.driver.find_element_by_link_text("ALL Journals")
                except:
                    logging.error("Not Loaded")
                else:
                    is_citing_journal_clicked = True
        logging.info("Operation successful")

    def get_citing_data(self):
        # Get cited journal data
        logging.info("Getting citing data...")
        table = self.soup.find(id='citingJournalData').find('tbody')
        rows = table.find_all('tr')
        ALL = []
        YEAR_2016 = []
        temp_dict = dict()
        for row in rows:
            cells = row.find_all('td')
            name = cells[2].text
            if name in self.journals_dict:
                value = cells[3].text
                value_2016 = cells[4].text
            else:
                value = "0"
                value_2016 = "0"
            temp_dict[name] = {
                "ALL": value,
                "2016": value_2016
            }
            logging.info("Citing {} in all years : {} times".format(name, value))
            logging.info("Citing {} in 2016 : {} times".format(name, value_2016))
        for key in self.journals_list:
            if key in temp_dict:
                ALL.append(temp_dict[key]['ALL'])
                YEAR_2016.append(temp_dict[key]['2016'])
            else:
                ALL.append("0")
                YEAR_2016.append("0")
        return ALL, YEAR_2016

    def get_soup(self):
        html = self.driver.find_element_by_tag_name('html').get_attribute('innerHTML')
        self.soup = BeautifulSoup(html, 'html.parser')


    def main(self):
        start_time = time.time()
        for i in range(10):
            self.login()
            END_INDEX = min(START_INDEX + 50, TOTAL_JOURNAL)
            for main_journal in self.journals_list[START_INDEX:END_INDEX]:
                self.csv.write(main_journal + ",")
                self.csv_2016.write(main_journal + ",")
                self.select_journal(main_journal)
                self.get_soup()
                ALL, YEAR_2016 = self.get_citing_data()
                self.csv.write(",".join(ALL))
                self.csv_2016.write(",".join(YEAR_2016))
                self.csv.write("\n")
                self.csv_2016.write("\n")
                self.driver.get("https://jcr-incites-thomsonreuters-com.libproxy1.nus.edu.sg/JCRJournalHomeAction.action?year=&edition=&journal=")
            START_INDEX += 30
            self.driver.close()

        self.csv.close()
        self.csv_2016.close()
        elapsed_time = time.time() - start_time
        logging.info("Elapsed time: {}".format(time.strftime("%H:%M:%S", time.gmtime(elapsed_time))))
        self.driver.close()


if __name__ == '__main__':
    sc = Scrapper()
    sc.main()
