from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from kafka import KafkaProducer
from utils.yaml_loader import yaml_kafka_host_loader
from datetime import datetime
import json

#global variables
action_types = ["click", "search", "add_to_cart", "purchase", "product_unavailable"]
topics = ["page_loaded", "product_searched", "product_clicked", "warranty_selected", "added_to_cart", "product_availability", "product_variant_selected", "cart_viewed", "checking_out"]

def send_events_to_kafka(topic, event_data):
    producer_host = yaml_kafka_host_loader('../docker-compose.yaml')
    amazon_producer = KafkaProducer(bootstrap_servers=producer_host,
                             value_serializer=lambda v: json.dumps(v).encode('utf-8'))

    iso_string = datetime.utcnow().isoformat() + 'Z'
    dt_object = datetime.fromisoformat(iso_string.replace('Z', '+00:00'))

    event_payload = {
        "shopping_timestamp": dt_object,
        "action_type": event_data["action_type"],
        "target": event_data["target"],
        "value": event_data["value"],
        "url": event_data["url"]
    }
    amazon_producer.send(topic, event_payload)
    amazon_producer.flush()
    amazon_producer.close()

def simulate_user_shopping_event():
    chrome_option = Options()
    chrome_option.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_option)
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

    #Buying electronics and accessories to build ultimate gaming PC set up
    search_bar = WebDriverWait(driver, 3).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, ".nav-input.nav-progressive-attribute"))
    )

    search_bar.send_keys("hp omen 45l gaming desktop" + Keys.RETURN)
    event_dict["action_type"] = action_types[1]
    event_dict["value"] = "hp omen 45l gaming desktop search"
    event_dict["url"] = driver.current_url
    send_events_to_kafka(topics[1], event_dict)

    driver.implicitly_wait(3)
    desktop_option = driver.find_element(by=By.CSS_SELECTOR, value='div[data-component-id="3"] h2 a')
    desktop_option.click()
    event_dict["action_type"] = action_types[0]
    event_dict["target"] = "load-product-page-button"
    event_dict["value"] = "HP Omen 45L Desktop"
    event_dict["url"] = driver.current_url
    send_events_to_kafka(topics[2], event_dict)

    two_yr_warranty_checkbox = driver.find_element(by=By.ID, value="mbb-offeringID-1")
    two_yr_warranty_checkbox.click()
    event_dict["target"] = "warranty-option-button - mbb-offeringID-1"
    event_dict["value"] = "2 year warranty protection added"
    event_dict["url"] = driver.current_url
    send_events_to_kafka(topics[3], event_dict)

    wait = WebDriverWait(driver, 3)
    wait.until(EC.element_to_be_selected(two_yr_warranty_checkbox))

    desired_desktop_txt = driver.find_element(by=By.XPATH, value='//*[@id="availability"]/span')

    if "In Stock" in desired_desktop_txt:
        driver.find_element(by=By.ID, value="add-to-cart-button").click()
        event_dict["action_type"] = action_types[2]
        event_dict["target"] = "add-to-cart-button"
        event_dict["value"] = "2 year warranty protection added"
        event_dict["url"] = driver.current_url
        send_events_to_kafka(topics[4], event_dict)
    else:
        event_dict["action_type"] = action_types[4]
        event_dict["target"] = "availability_text"
        event_dict["value"] = "Out of Stock"
        event_dict["url"] = driver.current_url

    send_events_to_kafka(topics[5], event_dict)

    """
    if clear() doesn't work
    """
    search_bar.send_keys(Keys.CONTROL + "a")
    search_bar.send_keys(Keys.DELETE)
    search_bar.send_keys("hp omen 32 inch curved gaming monitor" + Keys.RETURN)
    event_dict["action_type"] = action_types[1]
    event_dict["target"] = "nav-input"
    event_dict["value"] = "HP Omen 32 inch curved gaming monitor search"
    event_dict["url"] = driver.current_url
    send_events_to_kafka(topics[1], event_dict)

    driver.implicitly_wait(3)

    desired_curved_monitor_title = driver.find_element(by=By.XPATH, value='//h2/span[contains(text(), "OMEN 32c QHD 165Hz Curved Gaming Monitor")]')
    results = driver.find_elements(By.CSS_SELECTOR, "div[role='listitem']")
    for result in results:
        if desired_curved_monitor_title.text in result.text:
            #Added to cart
            driver.find_element(by=By.ID, value="a-autoid-1-announce").click()
            event_dict["action_type"] = action_types[2]
            event_dict["target"] = "add-to-cart-button"
            event_dict["value"] = "HP Omen 32 inch curved gaming monitor"
            event_dict["url"] = driver.current_url
            send_events_to_kafka(topics[4], event_dict)

    """
    if clear() doesn't work
    """
    search_bar.send_keys(Keys.CONTROL + "a")
    search_bar.send_keys(Keys.DELETE)
    search_bar.send_keys("hp RGB wired gaming keyboard and mouse" + Keys.RETURN)
    event_dict["action_type"] = action_types[1]
    event_dict["target"] = "nav-input"
    event_dict["value"] = "RGB Backlit Wired Gaming Keyboard and Mouse Combo search"
    event_dict["url"] = driver.current_url
    send_events_to_kafka(topics[1], event_dict)

    driver.implicitly_wait(3)
    driver.find_element(by=By.ID, value="a-autoid-3-announce").click()
    event_dict["action_type"] = action_types[2]
    event_dict["target"] = "add-to-cart-button"
    event_dict["value"] = "RGB Backlit Wired Gaming Keyboard and Mouse Combo"
    event_dict["url"] = driver.current_url
    send_events_to_kafka(topics[4], event_dict)

    """
    if clear() doesn't work
    """
    search_bar.send_keys(Keys.CONTROL + "a")
    search_bar.send_keys(Keys.DELETE)

    search_bar.send_keys("gaming cloud arm rest" + Keys.RETURN)
    event_dict["action_type"] = action_types[1]
    event_dict["target"] = "nav-input"
    event_dict["value"] = "gaming cloud arm rest search"
    event_dict["url"] = driver.current_url
    send_events_to_kafka(topics[1], event_dict)

    cloud_rest_page = driver.find_element(by=By.PARTIAL_LINK_TEXT, value="JIKIOU Upgrade Leather Cloud Keyboard")
    cloud_rest_page.click()
    event_dict["action_type"] = action_types[2]
    event_dict["target"] = "load-product-page-button"
    event_dict["value"] = "JIKIOU Upgrade Leather Cloud Keyboard Wrist Rest page"
    event_dict["url"] = driver.current_url
    send_events_to_kafka(topics[2], event_dict)

    rainbow02 = driver.find_element(by=By.ID, value="color_name_1")

    if rainbow02.is_selected():
        print("Button is already selected")
    else:
        rainbow02.click()

    event_dict["action_type"] = action_types[0]
    event_dict["target"] = "color-variant-selected"
    event_dict["value"] = "JIKIOU Upgrade Leather Cloud Keyboard Wrist Rest variant"
    event_dict["url"] = driver.current_url
    send_events_to_kafka(topics[0], event_dict)
    send_events_to_kafka(topics[6], event_dict)

    driver.find_element(by=By.ID, value="add-to-cart-button").click()
    event_dict["action_type"] = action_types[2]
    event_dict["target"] = "add-to-cart-button"
    event_dict["value"] = "JIKIOU Upgrade Leather Cloud Keyboard Wrist Rest"
    event_dict["url"] = driver.current_url
    send_events_to_kafka(topics[4], event_dict)

    """
    if clear() doesn't work
    """
    search_bar.send_keys(Keys.CONTROL + "a")
    search_bar.send_keys(Keys.DELETE)
    search_bar.send_keys("funny mouse pad" + Keys.RETURN)
    event_dict["action_type"] = action_types[1]
    event_dict["target"] = "nav-input"
    event_dict["value"] = "funny mouse pad search"
    event_dict["url"] = driver.current_url
    send_events_to_kafka(topics[1], event_dict)

    driver.implicitly_wait(3)

    driver.find_element(by=By.ID, value="a-autoid-49-announce").click()
    event_dict["action_type"] = action_types[2]
    event_dict["target"] = "add-to-cart-button"
    event_dict["value"] = "Jakayla Cute Funny Mouse Pad Round"
    event_dict["url"] = driver.current_url
    send_events_to_kafka(topics[4], event_dict)

    """
    if clear() doesn't work
    """
    search_bar.send_keys(Keys.CONTROL + "a")
    search_bar.send_keys(Keys.DELETE)
    search_bar.send_keys("wireless cat ear gaming headset" + Keys.RETURN)
    event_dict["action_type"] = action_types[1]
    event_dict["target"] = "nav-input"
    event_dict["value"] = "wireless cat ear gaming headset search"
    event_dict["url"] = driver.current_url
    send_events_to_kafka(topics[1], event_dict)

    WebDriverWait(driver,5).until(
        EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Wireless Cat Ear Headphones, Pink Gaming Headset Bluetooth 5.0"))
    ).click()
    event_dict["action_type"] = action_types[0]
    event_dict["target"] = "load-product-page-button"
    event_dict["value"] = "Wireless Cat Ear Headphones, Pink Gaming Headset Bluetooth 5.0 page"
    event_dict["url"] = driver.current_url
    send_events_to_kafka(topics[2], event_dict)

    available_headset_txt = WebDriverWait(driver, 5).until(
        EC.visibility_of_element_located((By.XPATH, '//*[@id="availability"]/span'))
    )

    if "In Stock" in available_headset_txt:
        driver.find_element(by=By.ID, value="add-to-cart-button").click()
        event_dict["action_type"] = action_types[0]
        event_dict["target"] = "add-to-cart-button"
        event_dict["value"] = "Wireless Cat Ear Headphones, Pink Gaming Headset"
        event_dict["url"] = driver.current_url
        send_events_to_kafka(topics[4], event_dict)
    else:
        event_dict["action_type"] = action_types[4]
        event_dict["target"] = "availability_text"
        event_dict["value"] = "Out of Stock"
        event_dict["url"] = driver.current_url

    send_events_to_kafka(topics[5], event_dict)
    cart = WebDriverWait(driver, 3).until(
        EC.element_to_be_clickable((By.ID, "nav-cart"))
    )

    cart.click()
    event_dict["action_type"] = action_types[0]
    event_dict["target"] = "cart-button"
    event_dict["value"] = "cart full"
    event_dict["url"] = driver.current_url
    send_events_to_kafka(topics[7], event_dict)

    WebDriverWait(driver, 3).until(
        EC.element_to_be_clickable((By.NAME, "proceedToRetailCheckout"))
    ).click()
    event_dict["action_type"] = action_types[3]
    event_dict["target"] = "proceed-to-checkout-button"
    event_dict["value"] = "purchasing"
    event_dict["url"] = driver.current_url
    send_events_to_kafka(topics[8], event_dict)

    driver.quit()

def simulate_user_luxury_window_shopping_event():
    chrome_option = Options()
    chrome_option.add_argument("--headless")
    ws_driver = webdriver.Chrome(options=chrome_option)
    #errors = ["NoSuchElementException", "ElementNotInteractableException"]
    ws_driver.get("https://www.amazon.com")

    amazon_title = ws_driver.title
    print(f'Sending event: Page title - {amazon_title}')
    event_dict = {
        "action_type": action_types[0],
        "target": "nav-input",
        "value": f'Home Page engagement - {amazon_title}',
        "url": ws_driver.current_url
    }

    send_events_to_kafka(topics[0], event_dict)

    #Random window shopping
    search_bar = WebDriverWait(ws_driver, 3).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, ".nav-input.nav-progressive-attribute"))
    )

    search_bar.send_keys("versace sunglasses for men" + Keys.RETURN)
    event_dict["action_type"] = action_types[1]
    event_dict["target"] = "nav-input"
    event_dict["value"] = "versace sunglasses for men search"
    event_dict["url"] = ws_driver.current_url
    send_events_to_kafka(topics[1], event_dict)

    results = ws_driver.find_elements(By.CSS_SELECTOR, "div[role='listitem']")

    for result in results:
        product_name_descript = result.text
        if "Mens Sunglasses (VE4296) Acetate" in product_name_descript:
            WebDriverWait(ws_driver, 3).until(
                EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Mens Sunglasses (VE4296) Acetate"))
            ).click()
            event_dict["action_type"] = action_types[0]
            event_dict["target"] = "load-product-page-button"
            event_dict["value"] = "Versace Mens Sunglasses (VE4296) Acetate page"
            event_dict["url"] = ws_driver.current_url
            send_events_to_kafka(topics[2], event_dict)

    """
    if clear() doesn't work
    """
    search_bar.send_keys(Keys.CONTROL + "a")
    search_bar.send_keys(Keys.DELETE)

    search_bar.send_keys("marc jacobs bag for women" + Keys.RETURN)
    event_dict["action_type"] = action_types[1]
    event_dict["target"] = "nav-input"
    event_dict["value"] = "marc jacobs bag for women search"
    event_dict["url"] = ws_driver.current_url
    send_events_to_kafka(topics[1], event_dict)

    WebDriverWait(ws_driver, 3).until(
        EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Snapshot, Black"))
    ).click()
    event_dict["action_type"] = action_types[0]
    event_dict["target"] = "load-product-page-button"
    event_dict["value"] = "marc jacobs bag for women page"
    event_dict["url"] = ws_driver.current_url
    send_events_to_kafka(topics[2], event_dict)

    ws_driver.find_element(by=By.NAME, value="18").click()
    event_dict["action_type"] = action_types[0]
    event_dict["target"] = "load-product-page-button"
    event_dict["value"] = "marc jacobs bag for women page"
    event_dict["url"] = ws_driver.current_url
    send_events_to_kafka(topics[0], event_dict)

    ws_driver.find_element(by=By.NAME, value="11").click()
    event_dict["action_type"] = action_types[0]
    event_dict["target"] = "load-product-page-button"
    event_dict["value"] = "marc jacobs bag for women page"
    event_dict["url"] = ws_driver.current_url
    send_events_to_kafka(topics[0], event_dict)

    WebDriverWait(ws_driver, 3).until(
        EC.visibility_of_element_located((By.PARTIAL_LINK_TEXT, "Saks"))
    ).click()
    event_dict["action_type"] = action_types[0]
    event_dict["target"] = "nav-main"
    event_dict["value"] = "Saks page"
    event_dict["url"] = ws_driver.current_url
    send_events_to_kafka(topics[0], event_dict)

    wait = WebDriverWait(ws_driver, 5)

    results_list = ws_driver.find_elements(by=By.CLASS_NAME, value="ASINCarouselItem__asinslide__qRPqK")
    carrot_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[aria-label="Click to slide right"]')))
    for result in results_list:
        if "Glass Crystal Monogram Clip-On Stud Earrings" in result.text:
            WebDriverWait(ws_driver, 3).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "Title_title_z5HRm"))
            ).click()
            event_dict["action_type"] = action_types[0]
            event_dict["target"] = "Dolce & Gabbana Goldtone Or Silvertone & Glass Crystal Monogram Clip-On Stud Earrings"
            event_dict["value"] = "Saks page"
            event_dict["url"] = ws_driver.current_url
            send_events_to_kafka(topics[2], event_dict)
        else:
            carrot_button.click()
            event_dict["action_type"] = action_types[0]
            event_dict["target"] = "Carousel-right-button-click"
            event_dict["value"] = "Saks page"
            event_dict["url"] = ws_driver.current_url
            send_events_to_kafka(topics[0], event_dict)

    ws_driver.quit()

if __name__ == "__main__":
    for i in range(5):
        simulate_user_luxury_window_shopping_event()
        if i == 3:
            simulate_user_shopping_event()