from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.webdriver.chrome.options import Options


def init_driver():
    # Initiate the driver
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(chrome_options=options)

    # Set a default wait time for the browser [5 seconds here]
    driver.wait = WebDriverWait(driver, 5)

    return driver


def close_driver(driver):
    driver.close()


def login_twitter(driver, username, password):
    # Open the web page in the browser:
    driver.get("https://twitter.com/login")

    # Find the boxes for username and password
    username_field = driver.find_element_by_class_name("js-username-field")
    password_field = driver.find_element_by_class_name("js-password-field")

    # Enter username
    username_field.send_keys(username)

    time.sleep(2)

    # Enter password
    password_field.send_keys(password)
    time.sleep(2)

    # Click the "Log In" button
    driver.find_element_by_class_name("EdgeButtom--medium").click()


def make_poll(driver, text, choice1, choice2, choice3, choice4):

    # Write the poll text
    tweet = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div[id='tweet-box-home-timeline']")))
    tweet.send_keys(text)

    # Click the poll button
    time.sleep(2)
    driver.find_element_by_class_name("PollCreator-btn").click()

    comp = driver.find_element_by_class_name("TweetBoxAttachments").find_element_by_class_name("CardComposer").find_element_by_class_name("PollingCardComposer")

    # Write card 1
    time.sleep(2)
    box = comp.find_element_by_class_name("PollingCardComposer-option1").find_element_by_class_name("PollingCardComposer-optionInput")
    box.send_keys(choice1)

    # Write card 2
    time.sleep(2)
    box = comp.find_element_by_class_name("PollingCardComposer-option2").find_element_by_class_name("PollingCardComposer-optionInput")
    box.send_keys(choice2)

    # Add card 3
    time.sleep(2)
    comp.find_element_by_class_name("PollingCardComposer-addOption").click()

    # Write card 3
    time.sleep(2)
    box = comp.find_element_by_class_name("PollingCardComposer-option3").find_element_by_class_name("PollingCardComposer-optionInput")
    box.send_keys(choice3)

    # Add card 4
    time.sleep(2)
    comp.find_element_by_class_name("PollingCardComposer-addOption").click()

    # Write card 4
    time.sleep(2)
    box = comp.find_element_by_class_name("PollingCardComposer-option4").find_element_by_class_name("PollingCardComposer-optionInput")
    box.send_keys(choice4)

    # Post the tweet
    time.sleep(2)
    tweet = driver.find_element_by_xpath("//span[@class='add-tweet-button ']//following-sibling::button[contains(@class,'tweet-action')]")
    tweet.click()
    time.sleep(2)
