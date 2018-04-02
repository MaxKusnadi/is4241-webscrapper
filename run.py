from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys

import time
import logging

NUS_ID = ""
NUS_PASSWORD = ""

LOGIN_LINK = "https://proxylogin.nus.edu.sg/libproxy1/public/login.asp?logup=false&url=https://jcr.incites.thomsonreuters.com"
JOURNAL_TEXT = "journals.txt"
CSV_ALL_RESULT = "result_all.csv"
CSV_2016_RESULT = "result_2016.csv"

class Scrapper:

    def __init__(self):
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.journals = self._get_journals()
        self.csv, self.csv_2016 = self._get_csv()
        self.driver = self._get_driver()

    def _get_journals(self):
        # Reading journals
        logging.info("Getting journal info")
        journals = []
        with open(JOURNAL_TEXT, 'r') as f:
            for line in f:
                journals.append(line.strip())
        return journals

    def _get_csv(self):
        logging.info("Preparing CSV file")
        csv = open(CSV_ALL_RESULT, 'w')
        csv.write("Journal Name,")
        csv.write(",".join(self.journals))
        csv.write("\n")

        csv_2016 = open(CSV_2016_RESULT, 'w')
        csv_2016.write("Journal Name,")
        csv_2016.write(",".join(self.journals))
        csv_2016.write("\n")

        return csv, csv_2016

    def _get_driver(self):
        # Creating drive
        logging.info("Initializing the driver")
        driver = webdriver.Chrome('./chromedriver')
        driver.implicitly_wait(30)
        driver.maximize_window()
        return driver

    def login(self):
        # Trying to login
        logging.info("Signing in to the system")
        self.driver.get(LOGIN_LINK)
        domain = Select(self.driver.find_element_by_name("domain"))
        domain.select_by_value("NUSSTU")

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
        self.driver.find_element_by_class_name("checkbox-journals").click()
        journal_search = self.driver.find_element_by_name("journalSearch-inputEl")
        journal_search.send_keys(journal)
        journal = self.driver.find_element_by_class_name("x-boundlist-item")
        journal_name = journal.text
        succeed = False
        if not succeed:
            try:
                journal.click()
            except:
                journal_search.clear()
                journal_search.send_keys("journal")
                self.driver.find_element_by_class_name("x-boundlist-item").clic()
            else:
                succeed = True

        self.driver.find_element_by_link_text('Submit').click()
        self.driver.find_element_by_link_text(journal_name).click()
        logging.info("Operation successful")

    def get_citing_data(self, journal):
        # Get cited journal data
        logging.info("Getting citing journal data of {}".format(journal))
        self.driver.find_element_by_link_text("Citing Journal Data").click()
        try:
            row = self.driver.find_element_by_link_text(journal)
        except:
            logging.error("Journal {} not found".format(journal))
            return 0, 0
        else:
            alter = row.find_element_by_xpath("../../..")
            rows = alter.find_elements_by_tag_name("td")
            try:
                value_all = rows[3].find_element_by_tag_name('a').text
            except:
                value_all = 0

            try:
                value_2016 = rows[4].find_element_by_tag_name('a').text
            except:
                value_2016 = 0

            return value_all, value_2016

    def main(self):
        start_time = time.time()
        self.login()
        for main_journal in self.journals:
            self.csv.write(main_journal + ",")
            self.csv_2016.write(main_journal + ",")
            self.select_journal(main_journal)
            ALL = []
            YEAR_2016 = []
            for sub_journal in self.journals:
                value, value_2016 = self.get_citing_data(sub_journal)
                logging.info("{} citing {} in all years : {} times".format(main_journal, sub_journal, value))
                logging.info("{} citing {} in 2016 : {} times".format(main_journal, sub_journal, value_2016))
                ALL.append(str(value))
                YEAR_2016.append(str(value_2016))
            self.csv.write(",".join(ALL))
            self.csv_2016.write(",".join(YEAR_2016))
            self.csv.write("\n")
            self.csv_2016.write("\n")
            self.driver.find_element_by_link_text("Home").click()

        self.csv.close()
        self.csv_2016.close()
        elapsed_time = time.time() - start_time
        logging.info("Elapsed time: {}".format(time.strftime("%H:%M:%S", time.gmtime(elapsed_time))))


if __name__ == '__main__':
    sc = Scrapper()
    sc.main()
