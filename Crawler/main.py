from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from time import sleep
from random import randint
from random import random
from datetime import datetime
import requests

# https://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size
def readable_size(num, suffix='B'):
    for unit in ['','K','M','G','T','P','E','Z']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


def current_datetime():
    now = datetime.now()
    return now.strftime("%d-%m-%Y %H-%M-%S")


start_datetime = current_datetime()


def log_activity(message):
    print(message)
    log_file_object = open("./Crawler/Log/activity_log_" + start_datetime + ".txt", "a+")
    log_file_object.write(message)
    log_file_object.close()


pager_link = "https://obcan.justice.sk/infosud?p_p_id=isufront_WAR_isufront&p_p_col_id=column-1&p_p_col_count=1&p_p_mode=view&_isufront_WAR_isufront_view=list&p_p_state=normal&_isufront_WAR_isufront_entityType=rozhodnutie&_isufront_WAR_isufront_cur="

profile = webdriver.FirefoxProfile()
profile.set_preference("browser.download.folderList", 2)
profile.set_preference("browser.download.manager.showWhenStarting", False)
profile.set_preference("browser.download.dir", "D:/Rozsudky")
profile.set_preference("browser.helperapps.neverAsk.saveToDisk", "application/octet-stream,application/pdf")
driver = webdriver.Firefox(firefox_profile=profile)

driver.get("https://obcan.justice.sk/infosud/-/infosud/zoznam/rozhodnutie")

page_counter = 1
file_counter = 0
total_file_size = 0

while True:
    sleep(5)
    element_file_list_container = driver.find_element_by_id("_isufront_WAR_isufront_mapsSearchContainer")
    element_link_list = element_file_list_container.find_elements_by_tag_name("a")

    if random() < 0.03:
        break_time = randint(300, 600)
        log_activity(current_datetime() + " Taking a human-like break for %d seconds\n" % break_time)
        sleep(break_time)
        log_activity(current_datetime() + " Back to work\n")

    for element in element_link_list:
        sleep(randint(5, 12))
        driver.execute_script("arguments[0].scrollIntoView();", element)
        ActionChains(driver).key_down(Keys.CONTROL).click(element).key_up(Keys.CONTROL).perform()
        driver.switch_to.window(driver.window_handles[1])
        sleep(randint(5, 12))
        element_download_button = driver.find_element_by_class_name("documentDownload")

        req = requests.get(element_download_button.get_attribute("href"), allow_redirects=True)
        file_counter += 1
        open("D:/Rozsudky/" + str(file_counter) + ".pdf", 'wb').write(req.content)
        total_file_size += len(req.content)

        element_filename_container = driver.find_element_by_class_name("documentList")
        element_filename_label = element_filename_container.find_element_by_tag_name("h4")
        file_name = element_filename_label.text
        with open("./Crawler/file_ids.txt", "a") as file_object:
            file_object.write(str(file_counter) + " " + file_name + "\n")

        log_activity(current_datetime + "\nFile count: " + str(file_counter) + "\nTotal size " + readable_size(total_file_size))

        sleep(randint(22, 51))
        driver.close()
        driver.switch_to.window(driver.window_handles[0])

    sleep(randint(7, 20))
    page_counter = page_counter + 1
    driver.get(pager_link + str(page_counter))
