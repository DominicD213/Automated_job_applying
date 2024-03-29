
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
        except Exception:
            print("Error clicking on the Jobs tab:")

    def select_search_bar(self):
        try:
            search_bar_job = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.jobs-search-box__text-input')))
            search_bar_job.click()
            search_bar_job.clear()
            search_bar_job.send_keys(self.job_search)
            search_bar_job.send_keys(Keys.RETURN)

            time.sleep(1)

            location_search_bar = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.XPATH, '//*[@aria-label="City, state, or zip code"]')))
            location_search_bar.click()
            location_search_bar.clear()
            location_search_bar.send_keys(self.location)
            location_search_bar.send_keys(Keys.RETURN)
            print('Search bar clicked')
            time.sleep(2)

        except Exception:
            print("Error locating or interacting with the job search bar:")

    def job_filtering(self):
        try:
            easy_apply_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@aria-label="Easy Apply filter."]')))
            easy_apply_button.click()
        except Exception:
            print('Easy apply button not selected.')

        time.sleep(5)

        try:
            print("Clicking on Time Posted filter...")
            time_filter = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, '#searchFilter_timePostedRange, #searchFilter_timePostedRange-trigger')))
            time_filter.click()
            past_week = '//*[@for="timePostedRange-r604800"]'
            past_month = '//*[@for="timePostedRange-r2592000"]'
            time.sleep(1)
            past_week_option = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, past_month)))
            past_week_option.click()
            sumbition_filter = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@data-control-name="filter_show_results"]')))
            sumbition_filter.click()

            print("Selected 'Past Week' option successfully.")

        except TimeoutException:
            print("Timeout occurred while waiting for time posted filter.")
        except Exception as e:
            print("Error interacting with the time posted filter:", e)

        time.sleep(5)
        try:
            print("Clicking on Experience Level filter...")
            exp_filter = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.ID, 'searchFilter_experience')))
            exp_filter.click()
            time.sleep(1)
            for exp_level in ['experience-1', 'experience-2', 'experience-3']:
                exp_option = WebDriverWait(self.driver, 20).until(
                    EC.element_to_be_clickable((By.XPATH, f'//*[@for="{exp_level}"]')))
                exp_option.click()
                print(f"Selected {exp_level} option successfully.")
            time.sleep(1)
            exp_filter.send_keys(Keys.RETURN)
        except TimeoutException:
            print("Timeout occurred while waiting for experience level filter.")
        except Exception:
            print("Error interacting with the experience level filter:")

    def easy_Applying(self):
        try:
            total_results = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "display-flex.t-12.t-black--light.t-normal")))
            total_results_int = int(total_results.text.split(' ', 1)[0].replace(",", ""))
            print("Total results:", total_results_int)

            results = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME,
                                                     "ember-view.jobs-search-results__list-item.occludable-update.p0.relative.scaffold-layout__list-item")))

            self.apply_to_jobs(results)

            if total_results_int > 25:
                find_pages = self.driver.find_elements(By.CLASS_NAME, 'artdeco-pagination__indicator')
                total_pages_int = len(find_pages)

                for page_num in range(2, total_pages_int + 1):
                    try:
                        time.sleep(2)
                        page_button_xpath = f"//button[@aria-label='Page {page_num}']"
                        page_button = WebDriverWait(self.driver, 20).until(
                            EC.element_to_be_clickable((By.XPATH, page_button_xpath))
                        )
                        print(f"Moving to page {page_num}...")
                        page_button.click()
                        time.sleep(2)
                    except Exception as e:
                        print(f"An error occurred while navigating to page {page_num}: {str(e)}")

                    results = WebDriverWait(self.driver, 20).until(
                        EC.presence_of_all_elements_located((By.CLASS_NAME,
                                                                "ember-view.jobs-search-results__list-item.occludable-update.p0.relative.scaffold-layout__list-item")))
                    self.apply_to_jobs(results)

                    # Check if there's a "Next" button available
                    if total_results_int > 8 and page_num == total_pages_int:
                        next_button = self.driver.find_element(By.CLASS_NAME, "artdeco-pagination__button--next")
                        if next_button.is_enabled():
                            next_button.click()
                            time.sleep(2)
                            print("Moving to next set of pages...")
        except Exception as e:
            print("An error occurred:", str(e))

    def apply_to_jobs(self, results):
        for result in results:
            try:
                hover = ActionChains(self.driver).move_to_element(result)
                hover.perform()
                titles = result.find_elements(By.CLASS_NAME,
                                              'disabled.ember-view.job-card-container__link.job-card-list__title')
                time.sleep(1)
                for title in titles:
                    time.sleep(2)
                    self.submit_apply(title)
            except Exception as e:
                print("An error occurred while applying to a job:", str(e))

    def submit_apply(self, job_add):
        try:
            print('You are applying to the position of: ', job_add.text)
            job_add.click()
            time.sleep(1)
            in_apply = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME,
                                            'jobs-apply-button.artdeco-button.artdeco-button--3.artdeco-button--primary.ember-view')))

            if in_apply.text.strip() == 'Easy Apply':
                in_apply.click()
                print('Easy Apply button clicked')
                time.sleep(1)
            else:
                pass

            self.click_submit_button()

        except NoSuchElementException:
            print('You already applied to this job, go to next...')

        except Exception:
            print('Not direct application, going to next...')
            try:
                discard = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@data-test-modal-close-btn]")))
                discard.send_keys(Keys.RETURN)
                discard_confirm = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@data-test-dialog-primary-btn]")))
                discard_confirm.send_keys(Keys.RETURN)
            except NoSuchElementException:
                print('You already applied to this job, go to next...')
            except Exception:
                print('Moving to next Job')

    def click_submit_button(self):
        for _ in range(7):
            submit = self.driver.find_element(By.CLASS_NAME,
                                              'artdeco-button.artdeco-button--2.artdeco-button--primary.ember-view')
            time.sleep(1)

            # Get the text of specific elements on the page
            initial_results_texts = [element.text.strip() for element in
                                     self.driver.find_elements(By.CLASS_NAME, 'pl3.t-14.t-black--light')]
            time.sleep(1)  # Add a short delay to allow the page to load
            submit.click()
            # Refresh the elements to ensure we are not referencing stale elements
            updated_results_texts = [element.text.strip() for element in
                                     self.driver.find_elements(By.CLASS_NAME, 'pl3.t-14.t-black--light')]

            if '100%' in updated_results_texts:
                print("Updated value is 100. Clicking the submit button 2 more times.")
                for _ in range(2):
                    submit = self.driver.find_element(By.CLASS_NAME,
                                                      'artdeco-button.artdeco-button--2.artdeco-button--primary.ember-view')
                    submit.click()
                    time.sleep(1)
            else:
                print("Checking Progress Bar.")

            time.sleep(1)
            if initial_results_texts == updated_results_texts:
                print('No changes occurred after clicking submit. Stopping the application process.')
                return  # Exit the function if no changes occurred


    def quit_driver(self):
        self.driver.quit()

def main():
    username = 'dominicdigiacomo16@gmail.com'
    password = 'Autumngrace1!'
    job_search = ('Software Developer')
    location = ''

    linkedin_job_search = LinkedInJobSearch(username, password, job_search, location)
    linkedin_job_search.login()
    linkedin_job_search.click_jobs_tab()
    linkedin_job_search.select_search_bar()
    linkedin_job_search.job_filtering()
    time.sleep(2)
    linkedin_job_search.easy_Applying()
    linkedin_job_search.quit_driver()

if __name__ == "__main__":
    main()
