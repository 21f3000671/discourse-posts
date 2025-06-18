from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

# Initialize Selenium (Chrome)
service = Service('/usr/bin/chromedriver')
driver = webdriver.Chrome(service=service)

# Open login page
login_url = "https://discourse.onlinedegree.iitm.ac.in/login"
driver.get(login_url)

time.sleep(5)

# Fill credentials and submit
username = driver.find_element("id", "login-account-name")  # or "username", inspect HTML
password = driver.find_element("id", "login-account-password")
username.send_keys("21f3000671@ds.study.iitm.ac.in")
password.send_keys("BiI$_n2reSR|NwkoP~[E")
driver.find_element("id", "login-button").click()  # Adjust based on forum's HTML

# Wait for login to complete (check for a unique post-login element)
time.sleep(5)  # Or use WebDriverWait for dynamic content

# Extract cookies
cookies = driver.get_cookies()
print(cookies)
driver.quit()  # Close browser