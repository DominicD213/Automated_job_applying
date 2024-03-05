import re
from selenium import webdriver
from selenium.common import TimeoutException, NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class LinkedInJobSearch:
    def __init__(self, username, password, job_search, location):
        self.username = username
        self.password = password
        self.job_search = job_search
        self.location = location
        self.driver = self._initialize_driver()

    def _initialize_driver(self):
        options = webdriver.ChromeOptions()
        return webdriver.Chrome(options=options)

    def login(self):
        self.driver.get('https://www.linkedin.com')
        username_input = self.driver.find_element(By.ID, 'session_key')
        username_input.send_keys(self.username)
        password_input = self.driver.find_element(By.ID, 'session_password')
        password_input.send_keys(self.password)
        submit_button = self.driver.find_element(By.CLASS_NAME, 'sign-in-form__submit-btn--full-width')
        submit_button.click()

    def click_jobs_tab(self):
        try:
            jobs_tab = WebDriverWait(self.driver, 80).until(
                EC.presence_of_element_located((By.LINK_TEXT, 'Jobs')))
            self.driver.execute_script("arguments[0].scrollIntoView();", jobs_tab)
            jobs_tab.click()
            print('Jobs Tab clicked')
        except Exception as e:
            print("Error clicking on the Jobs tab:", e)

    def select_search_bar(self):
        try:
            search_bar_job = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.jobs-search-box__text-input')))
            search_bar_job.click()
            search_bar_job.clear()
            search_bar_job.send_keys(self.job_search)
            search_bar_job.send_keys(Keys.RETURN)

            location_search_bar = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.XPATH, '//*[@aria-label="City, state, or zip code"]')))
            location_search_bar.click()
            location_search_bar.clear()
            location_search_bar.send_keys(self.location)
            location_search_bar.send_keys(Keys.RETURN)
            print('Search bar clicked')

        except Exception as e:
            print("Error locating or interacting with the job search bar:", e)

    def job_filtering(self):
        try:
            easy_apply_button = WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@aria-label="Easy Apply filter."]'))
            )
            easy_apply_button.click()
        except Exception as e:
            print('Easy apply button not selected.', e)

        time.sleep(2)

        try:
            print("Clicking on Time Posted filter...")
        # Click on the "Time Posted" filter
            time_filter = WebDriverWait(self.driver, 80).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, '#searchFilter_timePostedRange, #searchFilter_timePostedRange-trigger')))
            time_filter.click()

        # Locate the "Past Week" option using a relative XPath expression
            past_week_option = WebDriverWait(self.driver, 80).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@for="timePostedRange-r604800"]'))
            )

            past_week_option.click()

            sumbition_filter = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@data-control-name="filter_show_results"]')))
            sumbition_filter.click()

            print("Selected 'Past Week' option successfully.")

        except TimeoutException:
            print("Timeout occurred while waiting for time posted filter.")
        except Exception as e:
            print("Error interacting with the time posted filter:", e)

        time.sleep(2)
        try:
            print("Clicking on Experience Level filter...")
            exp_filter = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.ID, 'searchFilter_experience')))
            exp_filter.click()
            for exp_level in ['experience-1', 'experience-2', 'experience-3']:
                exp_option = WebDriverWait(self.driver, 20).until(
                    EC.element_to_be_clickable((By.XPATH, f'//*[@for="{exp_level}"]')))
                exp_option.click()
                print(f"Selected {exp_level} option successfully.")
            exp_filter.send_keys(Keys.RETURN)
        except TimeoutException:
            print("Timeout occurred while waiting for experience level filter.")
        except Exception as e:
            print("Error interacting with the experience level filter:", e)

    def easy_Applying(self):
        try:
            total_results = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "display-flex.t-12.t-black--light.t-normal"))
            )
            total_results_int = int(total_results.text.split(' ', 1)[0].replace(",", ""))
            print("Total results:", total_results_int)

            time.sleep(2)
            # get results for the first page
            current_page = self.driver.current_url
            results = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME,
                    "ember-view.jobs-search-results__list-item.occludable-update.p0.relative.scaffold-layout__list-item"))
            )

            time.sleep(2)

            for result in results:
                hover = ActionChains(self.driver).move_to_element(result)
                hover.perform()
                titles = result.find_elements(By.CLASS_NAME,
                                              'disabled.ember-view.job-card-container__link.job-card-list__title')
                for title in titles:
                    self.submit_apply(title)

            if total_results_int > 25:
                time.sleep(2)

                find_pages = self.driver.find_elements(By.CLASS_NAME,'artdeco-pagination__pages.artdeco-pagination__pages--number')
                total_pages = find_pages[len(find_pages)-1].text
                total_pages_int = int(re.sub(r"[^\d.]", "", total_pages))
                get_last_page = self.driver.find_element(By.XPATH, "//button[@aria-label='Page "+str(total_pages_int)+"']")
                get_last_page.send_keys(Keys.RETURN)
                print(get_last_page)
                time.sleep(2)
                last_page = self.driver.current_url
                total_jobs = int(last_page.split('start=', 1)[1])



        except Exception as e:
            print("An error occurred:", str(e))  # Print the specific error message

    def submit_apply(self, job_add):
        """This function submits the application for the job add found"""

        print('You are applying to the position of: ', job_add.text)
        job_add.click()
        time.sleep(2)

        try:
            in_apply = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, 'jobs-apply-button.artdeco-button.artdeco-button--3.artdeco-button--primary.ember-view'))
            )
            in_apply.click()
            print('Easy Apply button clicked')
        except NoSuchElementException:
            print('You already applied to this job, go to next...')
            pass
        time.sleep(1)
        try:
            submit = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.CLASS_NAME, 'artdeco-button.artdeco-button--2.artdeco-button--primary.ember-view'))
            )
            submit.send_keys(Keys.RETURN)
            time.sleep(2)
            submit.send_keys(Keys.RETURN)
            time.sleep(2)

            review_button = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.CLASS_NAME, 'artdeco-button.artdeco-button--2.artdeco-button--primary.ember-view'))
            )
            review_button.send_keys(Keys.RETURN)
            time.sleep(2)
            final_submit = WebDriverWait(self.driver,20).until(
                EC.element_to_be_clickable((By.CLASS_NAME, 'artdeco-button.artdeco-button--2.artdeco-button--primary.ember-view'))
            )
            final_submit.send_keys(Keys.RETURN)


        # ... if not available, discard application and go to next
        except NoSuchElementException:
            print('Not direct application, going to next...')
            try:
                discard = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@data-test-modal-close-btn]"))
                )
                discard.send_keys(Keys.RETURN)
                time.sleep(1)
                discard_confirm = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@data-test-dialog-primary-btn]"))
                )
                discard_confirm.send_keys(Keys.RETURN)
                time.sleep(1)
            except NoSuchElementException:
                pass

    def quit_driver(self):
        self.driver.quit()

def main():
    username = ''
    password = ''
    job_search = 'Web Developer'
    location = 'United States'

    linkedin_job_search = LinkedInJobSearch(username, password, job_search, location)
    linkedin_job_search.login()
    time.sleep(2)
    linkedin_job_search.click_jobs_tab()
    linkedin_job_search.select_search_bar()
    time.sleep(2)
    linkedin_job_search.job_filtering()
    time.sleep(2)
    linkedin_job_search.easy_Applying()
    linkedin_job_search.quit_driver()

if __name__ == "__main__":
    main()
