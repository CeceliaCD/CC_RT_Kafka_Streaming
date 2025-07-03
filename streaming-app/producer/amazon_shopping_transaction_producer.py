from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import tempfile
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable
from datetime import datetime
import subprocess
import shutil
import os
import tempfile
import time
import json

import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

execution_logger = logging.getLogger('execution_tracker')
execution_logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

execution_logger.addHandler(console_handler)

try:
    subprocess.run(["pkill", "-f", "chrome"], check=False)
except Exception as e:
    execution_logger.debug(f"[WARN] Failed to kill chrome processes: {e}")

#global variables
#chrome_driver_path = Path(__file__).parent / "chromedriver" / "chromedriver-mac-x64" / "chromedriver"
service = Service(executable_path="/usr/bin/chromedriver")

action_types = ["click", "search", "add_to_cart", "purchase", "product_unavailable"]
topics = ["page_loaded", "product_searched", "product_clicked", "warranty_selected", "added_to_cart", "product_availability", "product_variant_selected", "cart_viewed", "checking_out"]

for _ in range(10):
    try:
        amazon_producer = KafkaProducer(bootstrap_servers="kafka:9092",
                                        api_version=(0, 11, 5),
                                        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                                        security_protocol="PLAINTEXT",
                                        acks='all',
                                        retries=5,
                                        retry_backoff_ms=1000,
                                        max_block_ms=120000,
                                        request_timeout_ms=30000)
        break
    except NoBrokersAvailable:
        time.sleep(5)
else:
    raise Exception("Kafka broker not available after multiple retries")

def send_events_to_kafka(topic, event_data):
    dt_object = datetime.utcnow().isoformat() + 'Z'

    event_payload = {
        "shopping_timestamp": dt_object,
        "action_type": event_data["action_type"],
        "target": event_data["target"],
        "value": event_data["value"],
        "url": event_data["url"]
    }

    try:
        amazon_producer.send(topic, event_payload).get(timeout=10)
        execution_logger.debug(f"Sent topic to kafka: {event_payload}")
    except Exception as e:
        execution_logger.error(f"Failed to send event to Kafka: {e}")
    amazon_producer.flush()

def simulate_user_shopping_event():
    chrome_data_dir = tempfile.mkdtemp()
    if os.path.exists(os.path.join(chrome_data_dir, 'SingletonLock')):
        os.remove(os.path.join(chrome_data_dir, 'SingletonLock'))

    chrome_option = Options()
    chrome_option.add_argument("--headless=new")
    chrome_option.add_argument(f"--user-data-dir={chrome_data_dir}")
    chrome_option.add_argument("--no-sandbox")
    chrome_option.add_argument("--disable-extensions")
    chrome_option.add_argument("--disable-dev-shm-usage")
    chrome_option.add_argument("--remote-debugging-port=9222")
    chrome_option.add_argument("--disable-gpu")
    chrome_option.add_argument("--disable-software-rasterizer")
    chrome_option.add_argument("--incognito")

    driver = webdriver.Chrome(service=service, options=chrome_option)
    #errors = ["NoSuchElementException", "ElementNotInteractableException"]
    driver.get("https://www.amazon.com")

    amazon_title = driver.title

    event_dict = {
        "action_type": action_types[0],
        "target": "nav-input",
        "value": f'Home Page engagement - {amazon_title}',
        "url": driver.current_url
    }

    send_events_to_kafka(topics[0], event_dict)
    execution_logger.debug(f"Sent topic to kafka: {event_dict}")

    WebDriverWait(driver, 20).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )

    print(driver.page_source)

    #Buying electronics and accessories to build ultimate gaming PC set up
    search_bar = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, '//input[@id="twotabsearchtextbox"]'))
    )

    search_bar.send_keys("hp omen 45l gaming desktop" + Keys.RETURN)
    event_dict["action_type"] = action_types[1]
    event_dict["value"] = "hp omen 45l gaming desktop search"
    event_dict["url"] = driver.current_url
    send_events_to_kafka(topics[1], event_dict)
    execution_logger.debug(f"Sent topic to kafka: {event_dict}")

    driver.implicitly_wait(5)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(5)
    desktop_option = driver.find_element(By.CSS_SELECTOR, 'a.a-link-normal.s-underline-text.s-underline-link-text.s-link-style.a-text-normal')
    desktop_option.click()
    event_dict["action_type"] = action_types[0]
    event_dict["target"] = "load-product-page-button"
    event_dict["value"] = "HP Omen 45L Desktop"
    event_dict["url"] = driver.current_url
    send_events_to_kafka(topics[2], event_dict)
    execution_logger.debug(f"Sent topic to kafka: {event_dict}")

    two_yr_warranty_checkbox = driver.find_element(by=By.ID, value="mbb-offeringID-1")
    two_yr_warranty_checkbox.click()
    event_dict["target"] = "warranty-option-button - mbb-offeringID-1"
    event_dict["value"] = "2 year warranty protection added"
    event_dict["url"] = driver.current_url
    send_events_to_kafka(topics[3], event_dict)
    execution_logger.debug(f"Sent topic to kafka: {event_dict}")

    wait = WebDriverWait(driver, 20)
    wait.until(EC.element_to_be_selected(two_yr_warranty_checkbox))

    driver.find_element(by=By.ID, value="add-to-cart-button").click()
    event_dict["action_type"] = action_types[2]
    event_dict["target"] = "add-to-cart-button"
    event_dict["value"] = "2 year warranty protection added"
    event_dict["url"] = driver.current_url
    send_events_to_kafka(topics[4], event_dict)
    execution_logger.debug(f"Sent topic to kafka: {event_dict}")

    send_events_to_kafka(topics[5], event_dict)
    execution_logger.debug(f"Sent topic to kafka: {event_dict}")

    """
    if clear() doesn't work
    """
    time.sleep(5)
    search_bar = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, '//input[@id="twotabsearchtextbox"]'))  # Replace with actual locator
    )
    search_bar.send_keys(Keys.CONTROL + "a")
    search_bar.send_keys(Keys.DELETE)
    search_bar.send_keys("hp omen 32 inch curved gaming monitor" + Keys.RETURN)
    event_dict["action_type"] = action_types[1]
    event_dict["target"] = "nav-input"
    event_dict["value"] = "HP Omen 32 inch curved gaming monitor search"
    event_dict["url"] = driver.current_url
    send_events_to_kafka(topics[1], event_dict)
    execution_logger.debug(f"Sent topic to kafka: {event_dict}")

    driver.implicitly_wait(5)
    #NOTE: REMOVE ALL TEXTS OF IN STOCK
    #Added to cart
    driver.find_element(by=By.ID, value="a-autoid-1-announce").click()
    event_dict["action_type"] = action_types[2]
    event_dict["target"] = "add-to-cart-button"
    event_dict["value"] = "HP Omen 32 inch curved gaming monitor"
    event_dict["url"] = driver.current_url
    send_events_to_kafka(topics[4], event_dict)
    execution_logger.debug(f"Sent topic to kafka: {event_dict}")

    """
    if clear() doesn't work
    """
    time.sleep(5)
    search_bar = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, '//input[@id="twotabsearchtextbox"]'))  # Replace with actual locator
    )
    search_bar.send_keys(Keys.CONTROL + "a")
    search_bar.send_keys(Keys.DELETE)
    search_bar.send_keys("hp RGB wired gaming keyboard and mouse" + Keys.RETURN)
    event_dict["action_type"] = action_types[1]
    event_dict["target"] = "nav-input"
    event_dict["value"] = "RGB Backlit Wired Gaming Keyboard and Mouse Combo search"
    event_dict["url"] = driver.current_url
    send_events_to_kafka(topics[1], event_dict)
    execution_logger.debug(f"Sent topic to kafka: {event_dict}")

    driver.implicitly_wait(5)
    driver.find_element(by=By.ID, value="a-autoid-3-announce").click()
    event_dict["action_type"] = action_types[2]
    event_dict["target"] = "add-to-cart-button"
    event_dict["value"] = "RGB Backlit Wired Gaming Keyboard and Mouse Combo"
    event_dict["url"] = driver.current_url
    send_events_to_kafka(topics[4], event_dict)
    execution_logger.debug(f"Sent topic to kafka: {event_dict}")

    """
    if clear() doesn't work
    """
    time.sleep(5)
    search_bar = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, '//input[@id="twotabsearchtextbox"]'))  # Replace with actual locator
    )
    search_bar.send_keys(Keys.CONTROL + "a")
    search_bar.send_keys(Keys.DELETE)

    search_bar.send_keys("gaming cloud arm rest" + Keys.RETURN)
    event_dict["action_type"] = action_types[1]
    event_dict["target"] = "nav-input"
    event_dict["value"] = "gaming cloud arm rest search"
    event_dict["url"] = driver.current_url
    send_events_to_kafka(topics[1], event_dict)
    execution_logger.debug(f"Sent topic to kafka: {event_dict}")

    try:
        cloud_rest_page = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "JIKIOU Upgrade Leather Cloud Keyboard"))
        )
        cloud_rest_page.click()
        event_dict["action_type"] = action_types[2]
        event_dict["target"] = "load-product-page-button"
        event_dict["value"] = "JIKIOU Upgrade Leather Cloud Keyboard Wrist Rest page"
        event_dict["url"] = driver.current_url
        send_events_to_kafka(topics[2], event_dict)
        execution_logger.debug(f"Sent topic to kafka: {event_dict}")

        rainbow02 = driver.find_element(by=By.ID, value="color_name_1")

        if rainbow02.is_selected():
            print("Button is already selected")
            execution_logger.debug(f"Button is already selected")
        else:
            rainbow02.click()

        event_dict["action_type"] = action_types[0]
        event_dict["target"] = "color-variant-selected"
        event_dict["value"] = "JIKIOU Upgrade Leather Cloud Keyboard Wrist Rest variant"
        event_dict["url"] = driver.current_url
        send_events_to_kafka(topics[0], event_dict)
        execution_logger.debug(f"Sent topic to kafka: {event_dict}")
        send_events_to_kafka(topics[6], event_dict)
        execution_logger.debug(f"Sent topic to kafka: {event_dict}")

        driver.find_element(by=By.ID, value="add-to-cart-button").click()
        event_dict["action_type"] = action_types[2]
        event_dict["target"] = "add-to-cart-button"
        event_dict["value"] = "JIKIOU Upgrade Leather Cloud Keyboard Wrist Rest"
        event_dict["url"] = driver.current_url
        send_events_to_kafka(topics[4], event_dict)
        execution_logger.debug(f"Sent topic to kafka: {event_dict}")
    except TimeoutException:
        print("Product not found, skipping...")

    """
    if clear() doesn't work
    """
    time.sleep(5)
    search_bar = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, '//input[@id="twotabsearchtextbox"]'))  # Replace with actual locator
    )
    search_bar.send_keys(Keys.CONTROL + "a")
    search_bar.send_keys(Keys.DELETE)
    search_bar.send_keys("funny mouse pad" + Keys.RETURN)
    event_dict["action_type"] = action_types[1]
    event_dict["target"] = "nav-input"
    event_dict["value"] = "funny mouse pad search"
    event_dict["url"] = driver.current_url
    send_events_to_kafka(topics[1], event_dict)
    execution_logger.debug(f"Sent topic to kafka: {event_dict}")

    driver.implicitly_wait(5)
    try:
        driver.find_element(by=By.ID, value="a-autoid-49-announce").click()
        event_dict["action_type"] = action_types[2]
        event_dict["target"] = "add-to-cart-button"
        event_dict["value"] = "Jakayla Cute Funny Mouse Pad Round"
        event_dict["url"] = driver.current_url
        send_events_to_kafka(topics[4], event_dict)
        execution_logger.debug(f"Sent topic to kafka: {event_dict}")
    except TimeoutException:
        print("Product not found, skipping...")

    """
    if clear() doesn't work
    """
    time.sleep(5)
    search_bar = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, '//input[@id="twotabsearchtextbox"]'))  # Replace with actual locator
    )
    search_bar.send_keys(Keys.CONTROL + "a")
    search_bar.send_keys(Keys.DELETE)
    search_bar.send_keys("wireless cat ear gaming headset" + Keys.RETURN)
    event_dict["action_type"] = action_types[1]
    event_dict["target"] = "nav-input"
    event_dict["value"] = "wireless cat ear gaming headset search"
    event_dict["url"] = driver.current_url
    send_events_to_kafka(topics[1], event_dict)
    execution_logger.debug(f"Sent topic to kafka: {event_dict}")

    try:
        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Wireless Cat Ear Headphones, Pink Gaming Headset Bluetooth 5.0"))
        ).click()
        event_dict["action_type"] = action_types[0]
        event_dict["target"] = "load-product-page-button"
        event_dict["value"] = "Wireless Cat Ear Headphones, Pink Gaming Headset Bluetooth 5.0 page"
        event_dict["url"] = driver.current_url
        send_events_to_kafka(topics[2], event_dict)
        execution_logger.debug(f"Sent topic to kafka: {event_dict}")

        driver.find_element(by=By.ID, value="add-to-cart-button").click()
        event_dict["action_type"] = action_types[0]
        event_dict["target"] = "add-to-cart-button"
        event_dict["value"] = "Wireless Cat Ear Headphones, Pink Gaming Headset"
        event_dict["url"] = driver.current_url
        send_events_to_kafka(topics[4], event_dict)
        execution_logger.debug(f"Sent topic to kafka: {event_dict}")
    except TimeoutException:
        print("Product not found, skipping...")

    send_events_to_kafka(topics[5], event_dict)
    execution_logger.debug(f"Sent topic to kafka: {event_dict}")
    cart = WebDriverWait(driver, 3).until(
        EC.element_to_be_clickable((By.ID, "nav-cart"))
    )

    cart.click()
    event_dict["action_type"] = action_types[0]
    event_dict["target"] = "cart-button"
    event_dict["value"] = "cart full"
    event_dict["url"] = driver.current_url
    send_events_to_kafka(topics[7], event_dict)
    execution_logger.debug(f"Sent topic to kafka: {event_dict}")

    WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.NAME, "proceedToRetailCheckout"))
    ).click()
    event_dict["action_type"] = action_types[3]
    event_dict["target"] = "proceed-to-checkout-button"
    event_dict["value"] = "purchasing"
    event_dict["url"] = driver.current_url
    send_events_to_kafka(topics[8], event_dict)
    execution_logger.debug(f"Sent topic to kafka: {event_dict}")

    driver.quit()


if __name__ == "__main__":
    simulate_user_shopping_event()
    amazon_producer.close()