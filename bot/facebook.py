"""Facebook Automatization with Selenium."""

from selenium.common.exceptions import TimeoutException
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait

from bot import db

login_url = "https://www.facebook.com/login"
apps_url = "https://developers.facebook.com/apps/"
settings_url = apps_url + "{}/settings/advanced/"

options = ChromeOptions()
options.use_chromium = True
options.headless = True
options.add_argument('--disable-infobars')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--window-size=1280,720')
options.add_argument('--disable-gpu')
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')


class CookiesSet:
	"""Wait until cookies are set."""

	cookie_count = 7

	def __call__(self, driver):
		return len(driver.get_cookies()) >= self.cookie_count


class AdAccounts:
	"""Wait until form appears."""

	def __call__(self, driver):
		return driver.find_element_by_id('advertiser_account_ids') or False


class SavingChanges:
	"""Wait until changes are saved and page reloaded."""

	def __call__(self, driver):
		return driver.execute_script('return window.pageYOffset') == 0


def with_driver(function):
	def connection(*args):
		driver = Chrome(options=options)
		try:
			return function(*args, driver)
		finally:
			driver.quit()
	return connection


@with_driver
def authorize(login, password, driver=None):
	driver.get(login_url)
	driver.find_element_by_id('email').send_keys(login)
	driver.find_element_by_id('pass').send_keys(password)
	driver.find_element_by_id('loginbutton').click()
	try:
		WebDriverWait(driver, 10).until(CookiesSet())
	except TimeoutException:
		driver.save_screenshot('data/bad.png')
		return False
	db.save_account(login, password, driver.get_cookies())
	driver.save_screenshot('data/good.png')
	return True


@with_driver
def update_app(app_id, new_ad_accounts_ids, driver=None):
	# restoring session
	account_id, session = db.get_account_session(app_id)
	driver.execute_cdp_cmd('Network.enable', {})
	for cookie in session:
		driver.execute_cdp_cmd('Network.setCookie', cookie)
	driver.execute_cdp_cmd('Network.disable', {})

	# loading app page
	url = settings_url.format(app_id)
	driver.get(url)
	ad_accounts = WebDriverWait(driver, 10).until(AdAccounts())

	# inputting new ad accounts
	driver.execute_script("arguments[0].scrollIntoView()", ad_accounts)
	ad_input = ad_accounts.find_elements_by_tag_name('input')[-1]
	for acc_id in new_ad_accounts_ids:
		ad_input.send_keys(acc_id)
		ad_input.send_keys(Keys.ENTER)
	driver.find_element_by_name('save_changes').click()
	WebDriverWait(driver, 10).until(SavingChanges())

	# checking result, updating session
	registered = set()
	for element in driver.find_elements_by_name('advertiser_account_ids[]'):
		registered.add(int(element.get_attribute('value')))
	db.save_session(account_id, driver.get_session())
	return registered
