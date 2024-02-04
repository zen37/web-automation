import time, os, re
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException


from amazon_constants import *

class ShoppingCartUpdateError(Exception):
    pass

def quit_driver(driver, source):
    print(f'Quitting Firefox driver... called from {source}')
    driver.quit()

#Step 1: Initialize WebDriver and Navigate to the Website
def get_driver_firefox():
    try:
        print('Initializing Firefox driver...')
        driver = webdriver.Firefox()
        driver.maximize_window()
        driver.get(WEBSITE)
        return driver
    except WebDriverException as e:
        print(f"Error initializing Firefox driver: {e}")
        # You can add additional error handling or log the error here
        return 

def get_folder_name():
    folder = datetime.now().strftime("%Y.%m.%d_%H.%M.%S")
    return folder

def save_screenshot(driver, folder, file_name):

    file_path = f"{SCREENSHOTS}/{folder}/{file_name}.png"
    #print("File path:", file_path)
    # Create the directory if it doesn't exist
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    try:
        driver.get_screenshot_as_file(file_path)
    except WebDriverException as e:
        print("Error occurred while taking screenshot:", e)

def check_text_results(driver):
    results_span = driver.find_element(By.XPATH, '//span[text()="Results"]')
    assert results_span, "Text 'Results' is not found on the page."

def get_description(item):
    description = item.text
    return description

def get_price(item):
    price_whole = item.find_element(By.XPATH, "//span[contains(@class,'a-price-whole')]")
    price_fraction = item.find_element('xpath', "(//span[contains(@class,'a-price-fraction')])")
    price = price_whole.text + "." + price_fraction.text

    return price

def navigate_to(driver, value):
    element = driver.find_element(by=By.ID, value=value)
    element.click()

def no_coverage(driver):
    try:
        # Wait for the obscuring element to become inactive
        WebDriverWait(driver, 10).until(
            EC.invisibility_of_element_located((By.CLASS_NAME, "a-button-input"))
        )

        # Find the target element
        element = driver.find_element(By.XPATH, '//*[@id="attachSiNoCoverage-announce"]')

        # Scroll the element into view
        driver.execute_script("arguments[0].scrollIntoView(true);", element)

        # Click the element
        element.click()
    except NoSuchElementException:
        # Handle the case when the element is not found
        print("Coverage not present")
    except StaleElementReferenceException:
        # Handle the case when the element reference is stale
        print("Element reference is stale. Try again.")
    except Exception as e:
        # Handle other exceptions
        print("Error occurred:", e)

def check_text_shopping_cart(driver):
    element = driver.find_element(By.XPATH, "//h1[contains(text(), 'Shopping Cart')]")
    assert "Shopping Cart" in element.text, "Text 'Shopping Cart' is not found on the page."

def get_description_cart(item):

    description_cart = item.text
    #Remove trailing ellipsis if present as amazon uses them to show the text has been truncated
    description_cart_no_ellipsis = re.sub(r'…+$', '', description_cart)

    return description_cart_no_ellipsis

def get_price_cart(item):
    price = item.text
    if price.startswith("$"):
        price = price[1:]
    return price

def update_shopping_cart(driver, quantity, folder):
    try:
        print(f"quantity {quantity}")

        # Find the dropdown element
        dropdown_element = WebDriverWait(driver, WAIT_TIME_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, "//span[@class='a-dropdown-label' and contains(text(), 'Qty')]"))
        )

        # Click on the dropdown element to open the options
        dropdown_element.click()

        # Wait for the options to be visible
        options = WebDriverWait(driver, WAIT_TIME_SECONDS).until(
            EC.visibility_of_all_elements_located((By.XPATH, "//a[@class='a-dropdown-link']"))
        )

        # Loop through the options to find and click the desired option
        for option in options:
            if option.text == str(quantity):
                option.click()
                break  # Stop looping once the desired option is clicked

    except TimeoutException as ex:
        save_screenshot(driver, folder, f"shopping_cart_update_{quantity}_TimeoutException")
        raise ShoppingCartUpdateError("Timeout occurred while waiting for elements") from ex

    except Exception as ex:
        raise ShoppingCartUpdateError("An error occurred during shopping cart update") from ex

def execute(driver):

    try:
        folder = get_folder_name()
        print("Folder for screenshots:", folder)

        current_url = driver.current_url
        print(f"Opening ... {current_url}")
        print(f"Searching for ... {SEARCH_FOR}")

        WebDriverWait(driver,WAIT_TIME_SECONDS).until(EC.visibility_of_element_located((By.ID, SEARCH_BOX)))

        #WebDriverWait(driver,WAIT_TIME_SECONDS).until(EC.visibility_of_element_located((By.XPATH,'//span[@id="twotabsearchtextbox"]')))
        search = driver.find_element(by=By.ID, value=SEARCH_BOX)
        #submit = driver.find_element(by=By.ID, value=SUBMIT_BUTTON)
        #submit.click()
        #Step 2: Search for a Product
        search.send_keys(SEARCH_FOR + Keys.RETURN)
        save_screenshot(driver, folder, SEARCH_FOR)

        driver.implicitly_wait(WAIT_TIME_SECONDS)

        #check we are in results page
        check_text_results(driver)

        time.sleep(TIME_SLEEP_SECONDS)
        #Step 3: Navigate to Product Listing Page
        first_result = driver.find_element(By.CSS_SELECTOR, "div.s-main-slot h2 span")
        description = get_description(first_result)
        price = get_price(first_result)
        # Print the product description
        print("First product in results list ...")
        print("Description:", description)
        print("Price:", price)
        save_screenshot(driver, folder, 'results')

        time.sleep(TIME_SLEEP_SECONDS)

        first_result.click()
        save_screenshot(driver, folder, 'first_item_details')

        time.sleep(TIME_SLEEP_SECONDS)
        #Step 4: Add Product to Cart
        navigate_to(driver, "add-to-cart-button")

        #no extra coverage warranty
        no_coverage(driver)

        time.sleep(TIME_SLEEP_SECONDS)
        #Step 5: Navigate to Shopping Cart
        ##Click on the cart icon to go to the Shopping Cart page.
        navigate_to(driver, "nav-cart-count-container")
        save_screenshot(driver, folder, 'shopping_cart')
        #check we are in the Shopping Cart
        check_text_shopping_cart(driver)

        ##Validate that the product from the Product Detail Page is listed in the cart.
        description_cart = get_description_cart(driver.find_element(By.CLASS_NAME, "a-truncate-cut"))
        price_cart = get_price_cart(driver.find_element(By.CSS_SELECTOR, "span.a-size-medium.a-color-base.sc-price.sc-white-space-nowrap.sc-product-price.a-text-bold"))

        print("Shopping Cart Product ...")
        print("Description:", description_cart)
        print("Price:", price_cart)

        #validate description (in shopping cart description is truncated)
        assert description.startswith(description_cart), "product description is not the same"
        #validate price
        assert price == price_cart, "product price is not the same"

        time.sleep(TIME_SLEEP_SECONDS)
        #Step 6: Update Shopping Cart
        ##Change the quantity of the product (e.g., increase from 1 to 2).
        qty = 2
        update_shopping_cart(driver, qty, folder)
        file_name = f"shopping_cart_update_quantity_{qty}"
        time.sleep(TIME_SLEEP_SECONDS)
        save_screenshot(driver, folder, file_name)

        ##Remove the extra product from the cart.
        qty = 1
        update_shopping_cart(driver, qty, folder)
        file_name = f"shopping_cart_update_quantity_{qty}"
        time.sleep(TIME_SLEEP_SECONDS)
        save_screenshot(driver, folder, file_name)

    except AssertionError as e:
        error_message = str(e)
        attribute = ""
        if "description" in error_message.lower():
            attribute = "description"
        elif "price" in error_message.lower():
            attribute = "price"

        save_screenshot(driver, folder, f"validate_product_{attribute}_AssertionError")
        print("Assert error:", e)
    except Exception as e:
        print("Error:", e)




if __name__ == '__main__':

    driver = get_driver_firefox()

    if driver:
        try:
            execute(driver)
        except Exception as e:
            print(f"Error: {e}")
            # You can add additional error handling or log the error here
        finally:
            quit_driver(driver, "main")
    else:
        quit_driver(driver, "main")
        print("Failed to initialize Firefox driver.")



"""
def get_driver_firefox_service():
    from selenium.webdriver.firefox.service import Service as FirefoxService
    # Specify the path to the GeckoDriver executable
    firefox_driver_path = '/path/to/geckodriver.exe'

    # Create a FirefoxService instance with the executable path
    firefox_service = FirefoxService(executable_path=firefox_driver_path)

    # Create a WebDriver instance using the FirefoxService
    driver = webdriver.Firefox(service=firefox_service)
"""

"""
    descriptions = driver.find_elements(By.XPATH,"//div[contains(@class,'s-matching-dir sg-col-16-of-20 sg-col sg-col-8-of-12 sg-col-12-of-16')]//span[@class='a-size-medium a-color-base a-text-normal']")
    prices_whole = driver.find_elements(By.XPATH,"//div[contains(@class,'s-matching-dir sg-col-16-of-20 sg-col sg-col-8-of-12 sg-col-12-of-16')]//span[@class='a-price-whole']")
    prices_fraction = driver.find_elements(By.XPATH,"//div[contains(@class,'s-matching-dir sg-col-16-of-20 sg-col sg-col-8-of-12 sg-col-12-of-16')]//span[@class='a-price-fraction']")

    print("First product in results list:")
    print("Description:", descriptions[0].text)
    print("Price:", prices_whole[0].text + "." + prices_fraction[0].text)

    
    for i in range(len(descriptions)):
        print(f"{i}st product in results list:")
        print("Description:", descriptions[i].text)  # Adjust index for 0-based list
        print("Price:", prices_whole[i].text + "." + prices_fraction[i].text)
        print()
    """