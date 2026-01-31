from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time

options = webdriver.ChromeOptions()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--remote-debugging-port=9222")
options.add_experimental_option("detach", True)

print("-- Step 1: Launch the FMSystems page in Chrome --")
try:
    driver = webdriver.Chrome(options=options)
    print("Chrome browser launched successfully")
except Exception as e:
    print(f"Error launching Chrome: {str(e)}")
    raise  # Re-raise the exception after printing it

LANDING_PAGE_URL = "https://fmsystems.cmu.edu/FMInteract/ShowDrawingView.aspx?file_code=L0&bldgcode%20floorcode%20optn=116%20%20%20%20%20%20%201%20%20%20&bldgcode=116%20%20%20%20%20%20%20&floorcode=1%20%20%20&act_code=Q#"
print("Navigating to landing page...")
try:
    driver.get(LANDING_PAGE_URL)
    print(f"Already navigated to {driver.current_url}. Please log in manually in the Chrome window.")
except Exception as e:
    print(f"Error navigating to URL: {str(e)}. Current URL: {driver.current_url}")

input("After you are fully logged in and you can see the main FMSystems UI, press Enter here to continue... ")

wait = WebDriverWait(driver, 30)

print("-- Step 2: Simulate Clicks --")

building_count = 0
floor_count = 0

def click_building_and_all_floors(wait, driver, building_label):
    global building_count, floor_count

    floor_links = wait.until(
        EC.presence_of_all_elements_located((
            By.XPATH,
            # only grab floors that belong to that building
            # find the <div> that contains the link of the building
            # then go to its following sibling <ul> and collect the rtIn links in that subtree
            f"//a[contains(normalize-space(.), '{building_label}')]/ancestor::div[1]/following-sibling::ul"
            "//div[contains(@class,'fmi-nav-floorplan')]/a[contains(@class,'rtIn')]"
        ))
    )

    if (not floor_links) or (len(floor_links) == 0):
        print(f"No floor links found under {building_label}, skipping.")
        return

    building_count += 1 # will not count buildings with zero floors
    floor_count += len(floor_links)

    home_window = driver.current_window_handle

    # Click every floor link one by one
    for idx in range(len(floor_links)):
        current_floor_links = driver.find_elements(
            By.XPATH,
            f"//a[contains(normalize-space(.), '{building_label}')]/ancestor::div[1]/following-sibling::ul"
            "//div[contains(@class,'fmi-nav-floorplan')]/a[contains(@class,'rtIn')]"
        )

        link = current_floor_links[idx]
        href = link.get_attribute("href")
        label = link.text.strip()

        print(f"Opening floor {label} ({idx+1}/{len(floor_links)}) -> {href}")
        # driver.get(href) # open url in same tab
        # open floor in new tab
        driver.execute_script("window.open(arguments[0], '_blank');", href)
        driver.switch_to.window(driver.window_handles[-1]) # Note: assumes new tab is last. Could be wrong if popups occur.

        # Handle possible modal alert: "Drawing file is not available!"
        try:
            WebDriverWait(driver, 1).until(EC.alert_is_present())
            alert = driver.switch_to.alert
            msg = alert.text
            alert.accept()
            print(f"Skipped floor {label or '(no label)'} due to alert: {msg}")
        except TimeoutException:
            # No alert -> give the site a moment to “warm” server-side state
            time.sleep(0.5)

        # close tab and return to main page
        driver.close()
        driver.switch_to.window(home_window)

    print(f"[DONE] Finished {building_label}; Finished {building_count} buildings with {floor_count} floors in total")

def js_click(el):
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
    driver.execute_script("arguments[0].click();", el)

def open_sites_and_expand_main_campus(wait):
    print("Ensuring Main Campus is expanded next building")
    show_menu = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.fmi-nav-2ndnav-show")))
    driver.execute_script("arguments[0].click();", show_menu)
    print("Clicked 'Show Menu'")
    time.sleep(0.2)

    campus_plus_xpath = (
        "//div[contains(@class,'rtTop') and "
        ".//a[contains(@class,'rtIn') and contains(., '00_Main Campus - Excludes Residences')]]"
        "//span[contains(@class,'rtPlus')]"
    )

    # 1. Try to find the plus sign for main campus section
    campus_plus = driver.find_elements(By.XPATH, campus_plus_xpath)

    if campus_plus:
        js_click(campus_plus[0])
        print("Clicked + to expand Main Campus section (already visible)")
        return

    # 2. Otherwise click Sites, then find +
    sites_link = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Sites")))
    sites_link.click()
    print("Clicked on 'Sites' link")

    campus_plus = wait.until(EC.element_to_be_clickable((By.XPATH, campus_plus_xpath)))
    js_click(campus_plus)
    print("Clicked + to expand Main Campus section")

def expand_building(wait, building_label):
    print(f"Expanding '{building_label}'...")
    linkElem = wait.until(
        EC.presence_of_element_located((
            By.XPATH,
            f"//a[contains(@class,'rtIn') and contains(normalize-space(.), '{building_label}')]"
        ))
    )

    driver.execute_script("arguments[0].scrollIntoView(true);", linkElem)
    time.sleep(0.2)

    plus = linkElem.find_element(By.XPATH, "preceding-sibling::span[contains(@class,'rtPlus')]")
    driver.execute_script("arguments[0].click();", plus)

    print(f"Clicked + to expand {building_label}.")
    time.sleep(0.5)

# List of buildings to click. Comment out any buildings you do not wish to process.
buildings_to_process = [
    # "Alumni House",
    # "ANSYS Hall",
    # "Baker-Porter Hall",
    # "Bramer House & Garage",
    # "College of Fine Arts",
    # "Cyert Hall",
    # "Dithridge Street Garage",
    # "Doherty Hall",
    # "East Campus Garage",
    # "Elliot Dunlap Smith Hall",
    # "Facilities Management Services (040)",
    # "Fifth Ave 4721",
    # "Fifth Ave 4802",
    # "Forbes Ave 4615",
    # "Gates and Hillman Centers & Garage",
    # "Gesling Stadium",
    # "Hall of the Arts",
    # "Hamburg Hall",
    # "Hamerschlag Hall",
    # "Henry St 4616",
    # "Henry St 4618",
    # "Henry St 4620",
    # "Highmark Center for Health, Wellness & Athletics",
    # "Hunt Library",
    # "Jared L. Cohon University Center",
    # "Landscape Support Facility",
    # "Margaret Morrison Carnegie Hall",
    # "Mellon Institute",
    # "Newell-Simon Hall",
    # "Posner Center",
    # "Posner Hall",
    # "Purnell Center for the Arts",
    # "Robert Mehrabian CIC",
    # "Roberts Engineering Hall",
    # "Scott Hall",
    # "South Craig St 203",
    # "South Craig St 205",
    # "South Craig St 300",
    # "South Craig St 311",
    # "South Craig St 407",
    # "South Craig St 417",
    # "South Neville Garage",
    # "TCS Hall & Garage",
    # "Tepper Building & Garage",
    # "UTDC",
    # "Warner Hall",
    # "Wean Hall",
]

open_sites_and_expand_main_campus(wait)
for building_label in buildings_to_process:
    expand_building(wait, building_label)
    click_building_and_all_floors(wait, driver, building_label)
