from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from time import sleep
from random import randint
from random import random
from datetime import datetime
import requests
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import NoSuchElementException
from math import floor

# https://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size
from selenium.webdriver.support.wait import WebDriverWait


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
file_path_head = "./Crawler/head.txt"
file_path_count = "./Crawler/count.txt"

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
no_break_counter = 0

head_file = None
existing_file_count = 0
pagination = 20
first_file_name = None

skip_count = 0
need_to_skip = False

with open(file_path_head, encoding="UTF-8") as curr_file:
    head_file = curr_file.readline()
with open(file_path_count) as curr_file:
    existing_file_count = int(curr_file.readline())

while True:
    sleep(5)

    element_file_list_container = driver.find_element_by_id("_isufront_WAR_isufront_mapsSearchContainer")
    element_link_list = element_file_list_container.find_elements_by_tag_name("a")

    if need_to_skip:
        element_link_list = element_link_list[skip_count:]
        need_to_skip = False
        skip_count = 0
        if first_file_name is not None:
            with open(file_path_head, "w+", encoding="UTF-8") as fp:
                fp.write(first_file_name)
            first_file_name = None

    if (random() < 0.03 and no_break_counter > 50) or no_break_counter > 200:
        break_time = randint(300, 600)
        log_activity(current_datetime() + " Taking a human-like break for %d seconds\n" % break_time)
        sleep(break_time)
        log_activity(current_datetime() + " Back to work\n")
        no_break_counter = 0

    for element in element_link_list:
        sleep(randint(5, 12))
        driver.execute_script("arguments[0].scrollIntoView();", element)
        ActionChains(driver).key_down(Keys.CONTROL).click(element).key_up(Keys.CONTROL).perform()
        driver.switch_to.window(driver.window_handles[1])

        sleep(randint(5, 12))

        element_download_button = None
        try:
            element = WebDriverWait(driver, 30).until(
                ec.presence_of_element_located((By.CLASS_NAME, "documentDownload"))
            )
            element_download_button = driver.find_element_by_class_name("documentDownload")
        except NoSuchElementException as E:
            log_activity(current_datetime() + " " + E.msg + "\n" + E.stacktrace)
            break

        req = requests.get(element_download_button.get_attribute("href"), allow_redirects=True)
        if req is not None and len(req.content) > 0:
            file_counter += 1
            no_break_counter += 1
            open("D:/Rozsudky/" + str(file_counter + existing_file_count) + ".pdf", 'wb').write(req.content)
            file_size = len(req.content)
            total_file_size += file_size

            element_filename_container = driver.find_element_by_class_name("documentList")
            element_filename_label = element_filename_container.find_element_by_tag_name("h4")
            file_name = element_filename_label.text

            if file_name == head_file:
                file_counter -= 1
                no_break_counter -= 1
                total_file_size -= file_size
                need_to_skip = True
                log_activity(current_datetime() + "\nNeed to skip %d files\n" % existing_file_count)

            if not need_to_skip:
                with open("./Crawler/file_ids.txt", "a") as file_object:
                    file_object.write(str(file_counter + existing_file_count) + " " + file_name + "\n")
                if first_file_name is None:
                    first_file_name = file_name

                log_activity(current_datetime() + "\nFile count: " + str(file_counter) + "\nTotal size " + readable_size(total_file_size))
                with open(file_path_count, "w+") as fp:
                    fp.write(str(existing_file_count + file_counter))

        sleep(randint(15, 30))
        driver.close()
        driver.switch_to.window(driver.window_handles[0])

        if need_to_skip:
            break

    if need_to_skip:
        page_counter = page_counter + int(floor(existing_file_count/float(pagination))) - 1
        skip_count = existing_file_count % pagination
    else:
        page_counter = page_counter + 1

    sleep(randint(7, 20))
    driver.get(pager_link + str(page_counter))
