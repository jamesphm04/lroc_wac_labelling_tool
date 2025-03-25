import os
import time
import random
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import InvalidArgumentException
from selenium.common.exceptions import ElementClickInterceptedException

class Scraper:
	# This time is used when we are waiting for element to get loaded in the html
	wait_element_time = 30

	def __init__(self, url):
		self.url = url

		self.setup_driver_options()
		self.setup_driver()

	# Automatically close driver on destruction of the object
	def __del__(self):
		self.driver.quit()

	def get_current_url(self):
		return self.driver.current_url
	# Add these options in order to make chrome driver appear as a human instead of detecting it as a bot
	# Also change the 'cdc_' string in the chromedriver.exe with Notepad++ for example with 'abc_' to prevent detecting it as a bot
	def setup_driver_options(self):
		self.driver_options = Options()

		download_folder = os.path.expanduser("~/MyFolder/code/GIT/ai4space_labelling_studio/BE/data")

		arguments = [
			'--disable-blink-features=AutomationControlled'
			# '--headless',
		]

		experimental_options = {
			'excludeSwitches': ['enable-automation', 'enable-logging'],
			'prefs': {
            'profile.default_content_setting_values.notifications': 2,
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
            'download.default_directory': download_folder,  # Set the download directory here
            'download.prompt_for_download': False,       # Disable the download prompt
            'directory_upgrade': True,                   # Automatically upgrade directory
            'safebrowsing.enabled': True                 # Enable safe browsing
			}}



		for argument in arguments:
			self.driver_options.add_argument(argument)

		for key, value in experimental_options.items():
			self.driver_options.add_experimental_option(key, value)

	# Setup chrome driver with predefined options
	def setup_driver(self):
		chrome_driver_path = ChromeDriverManager().install()
		self.driver = webdriver.Chrome(service=ChromeService(chrome_driver_path), options = self.driver_options)
		self.driver.get(self.url)
		self.driver.maximize_window()
  
  
	# Wait random amount of seconds before taking some action so the server won't be able to tell if you are a bot
	def wait_random_time(self):
		random_sleep_seconds = round(random.uniform(1, 2), 2)

		time.sleep(random_sleep_seconds)

	# Goes to a given page and waits random time before that to prevent detection as a bot
	def go_to_page(self, page):
		# Wait random time before refreshing the page to prevent the detection as a bot
		self.wait_random_time()

		# Refresh the site url with the loaded cookies so the user will be logged in
		self.driver.get(page)
		time.sleep(2)
		# self.scroll_down_and_back()
  

	def find_element(self, selector, exit_on_missing_element = True, wait_element_time = None):
		if wait_element_time is None:
			wait_element_time = self.wait_element_time

		# Intialize the condition to wait
		wait_until = EC.element_to_be_clickable((By.CSS_SELECTOR, selector))

		try:
			# Wait for element to load
			element = WebDriverWait(self.driver, wait_element_time).until(wait_until)
		except:
			if exit_on_missing_element:
				print('ERROR: Timed out waiting for the element with css selector "' + selector + '" to load')
				# End the program execution because we cannot find the element
				self.driver.refresh()
			else:
				return False

		return element

	def find_multiple_elements_by_xpath(self, xpath, index, exit_on_missing_element = True, wait_element_time = None):
		if wait_element_time is None:
			wait_element_time = self.wait_element_time

		# Intialize the condition to wait
		wait_until = EC.presence_of_all_elements_located((By.XPATH, xpath))

		try:
			# Wait for element to load
			elements = WebDriverWait(self.driver, wait_element_time).until(wait_until)
		except:
			if exit_on_missing_element:
				# End the program execution because we cannot find the element
				print('ERROR: Timed out waiting for the element with xpath "' + xpath + '" to load')
				self.driver.refresh()
			else:
				return False

		return elements[index]

	def find_element_by_xpath(self, xpath, exit_on_missing_element = True, wait_element_time = None):
		if wait_element_time is None:
			wait_element_time = self.wait_element_time

		# Intialize the condition to wait
		wait_until = EC.element_to_be_clickable((By.XPATH, xpath))

		try:
			# Wait for element to load
			element = WebDriverWait(self.driver, wait_element_time).until(wait_until)
		except:
			if exit_on_missing_element:
				# End the program execution because we cannot find the element
				print('ERROR: Timed out waiting for the element with xpath "' + xpath + '" to load')
				self.driver.refresh()
			else:
				return False

		return element

	# Wait random time before clicking on the element
	def element_click(self, selector, delay = True):
		if delay:
			self.wait_random_time()

		try:
			element = self.find_element(selector)
		except:
			print('ERROR: Timed out waiting for the element to load')
		if element: 
			element.click()

	# Wait random time before clicking on the element
	def element_click_by_xpath(self, xpath, delay = True):
		
     
		if delay:
			self.wait_random_time()
		try:
			element = self.find_element_by_xpath(xpath)
		except:
			print('ERROR: Timed out waiting for the element with xpath "' + xpath + '" to load')
		if element: 
			element.click()
	
	# Wait random time before sending the keys to the element
	def element_send_keys(self, selector, text, delay = True):
		if delay:
			self.wait_random_time()

		element = self.find_element(selector)

		try:
			element.click()
		except ElementClickInterceptedException:
			self.driver.execute_script("arguments[0].click();", element)
		self.wait_random_time()
		element.send_keys(text)

	# Wait random time before sending the keys to the element
	def element_send_keys_by_xpath(self, xpath, text, delay = True):
		if delay:
			self.wait_random_time()

		element = self.find_element_by_xpath(xpath)

		try:
			element.click()
		except ElementClickInterceptedException:
			self.driver.execute_script("arguments[0].click();", element)
		
		element.send_keys(text)

	def scroll_down_and_back(self):
		document_height = self.driver.execute_script("return document.body.scrollHeight")
		# Scroll down 100 pixels every 0.25 seconds
		for i in range(0, document_height, 100):
			self.driver.execute_script(f"window.scrollBy(0, {min(100, document_height - i)});")
			time.sleep(0.1)

		for i in range(document_height, 0, -100):
			self.driver.execute_script(f"window.scrollBy(0, -{min(100, i)});")
			time.sleep(0.1)
  
	def scroll_to_element(self, selector):
		element = self.find_element(selector)

		self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)

	def scroll_to_element_by_xpath(self, xpath):
		element = self.find_element_by_xpath(xpath)

		self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
  
	def element_delete_text(self, selector, delay = True):
			if delay:
				self.wait_random_time()

			element = self.find_element(selector)
			
			# Clear the textarea
			element.clear()