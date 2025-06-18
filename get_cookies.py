from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import pickle

def get_discourse_cookies():
    # Initialize browser
    driver = webdriver.Chrome(service=Service('/usr/bin/chromedriver'))
    
    # Open login page
    driver.get("https://discourse.onlinedegree.iitm.ac.in/login")
    time.sleep(5)  # Wait for page load

    # Fill credentials (update selectors as needed)
    driver.find_element("id", "login-account-name").send_keys("21f3000671@ds.study.iitm.ac.in")
    driver.find_element("id", "login-account-password").send_keys("BiI$_n2reSR|NwkoP~[E")
    driver.find_element("id", "login-button").click()
    time.sleep(5)  # Wait for login

    # Get cookies
    cookies = driver.get_cookies()
    driver.quit()
    
    # Save cookies
    with open('discourse_cookies.pkl', 'wb') as f:
        pickle.dump(cookies, f)
    
    print("Cookies saved successfully!")
    return cookies

if __name__ == "__main__":
    get_discourse_cookies()