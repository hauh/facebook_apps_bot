"""Facebook Automatization with Selenium."""

from selenium.common.exceptions import TimeoutException
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait

from bot import db

login_url = "https://www.facebook.com/login"
apps_url = "https://developers.facebook.com/apps/"
settings_url = apps_url + "{}/settings/advanced/"
centering_script = "arguments[0].scrollIntoView({block: 'center'});"

options = ChromeOptions()
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


class AdAccountsSection:
	"""Wait until form appears."""

	def __call__(self, driver):
		return driver.find_element_by_id('advertiser_account_ids') or False


class SavingChanges:
	"""Wait until changes are saved and page reloaded."""

	def __call__(self, driver):
		return driver.execute_script('return window.pageYOffset') == 0


def with_driver(function):
	def connection(**kwargs):
		driver = Chrome(options=options)
		try:
			return function(driver, **kwargs)
		finally:
			driver.quit()
	return connection


@with_driver
def authorize(driver, login, password):
	driver.get(login_url)
	driver.find_element_by_id('email').send_keys(login)
	driver.find_element_by_id('pass').send_keys(password)
	driver.find_element_by_id('loginbutton').click()
	try:
		WebDriverWait(driver, 10).until(CookiesSet())
	except TimeoutException:
		return False
	db.save_account(login, password, driver.get_cookies())
	return True


@with_driver
def update_app(driver, app_id, app_account, ad_accounts):
	# restoring session
	session = db.get_account_session(app_account)
	driver.execute_cdp_cmd('Network.enable', {})
	for cookie in session:
		driver.execute_cdp_cmd('Network.setCookie', cookie)
	driver.execute_cdp_cmd('Network.disable', {})

	# loading app page
	url = settings_url.format(app_id)
	driver.get(url)
	ads_section = WebDriverWait(driver, 10).until(AdAccountsSection())

	# inputting new ad accounts
	driver.execute_script(centering_script, ads_section)
	ad_section_input = ads_section.find_elements_by_tag_name('input')[-1]
	for ad_account_id in ad_accounts:
		ad_section_input.send_keys(ad_account_id)
		ad_section_input.send_keys(Keys.ENTER)
	driver.find_element_by_name('save_changes').click()
	WebDriverWait(driver, 10).until(SavingChanges())

	# checking result, updating session
	driver.refresh()
	registered = set()
	for element in driver.find_elements_by_name('advertiser_account_ids[]'):
		registered.add(int(element.get_attribute('value')))
	db.save_session(app_account, driver.get_cookies())
	return registered
