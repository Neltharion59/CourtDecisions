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
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from os.path import exists, isfile, join
from os import listdir
from os import getcwd
import sys

conf_path = getcwd()
sys.path.append(conf_path)
sys.path.append(conf_path + '..')
sys.path.append(conf_path + '../..')

from shared_info import file_pdf_directory
from shared_info import file_id_path

# https://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size
def readable_size(num, suffix='B'):
    for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
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
    log_file_object = open("./Log/activity_log_" + start_datetime + ".txt", "a+")
    log_file_object.write(message)
    log_file_object.close()


pager_link = "https://obcan.justice.sk/infosud?p_p_id=isufront_WAR_isufront&p_p_col_id=column-1&p_p_col_count=1&p_p_mode=view&_isufront_WAR_isufront_view=list&p_p_state=normal&_isufront_WAR_isufront_entityType=rozhodnutie&_isufront_WAR_isufront_delta=75&_isufront_WAR_isufront_cur="

profile = webdriver.FirefoxProfile()
profile.set_preference("browser.download.folderList", 2)
profile.set_preference("browser.download.manager.showWhenStarting", False)
profile.set_preference("browser.download.dir", file_pdf_directory)
profile.set_preference("browser.helperapps.neverAsk.saveToDisk", "application/octet-stream,application/pdf")
driver = webdriver.Firefox(firefox_profile=profile)

page_counter = 1
file_counter = 0
total_file_size = 0
no_break_counter = 0

existing_file_links = []
if exists(file_id_path):
    with open(file_id_path, "r", encoding='UTF-8') as file_object:
        for line in file_object:
            link = line.replace('\n', '').split(' ')[2]
            existing_file_links.append(link)

all_existing_id_list = [int(f.replace('.pdf', '')) for f in listdir(file_pdf_directory) if isfile(join(file_pdf_directory, f))]
existing_file_count = max(all_existing_id_list)

print(str(existing_file_count) + " files exists")

log_activity(current_datetime() + "\nHas {0} files\n".format(existing_file_count))
log_activity(current_datetime() + "\nStarting crawling session\n")

driver.get(pager_link + str(page_counter))

print('Proceeding to crawling')

while True:
    sleep(15)

    element_file_list_container = driver.find_element_by_id("_isufront_WAR_isufront_mapsSearchContainer")
    element_link_list = element_file_list_container.find_elements_by_tag_name("a")

    if (random() < 0.03 and no_break_counter > 50) or no_break_counter > 200:
        break_time = randint(300, 600)
        log_activity(current_datetime() + " Taking a human-like break for %d seconds\n" % break_time)
        sleep(break_time)
        log_activity(current_datetime() + " Back to work\n")
        no_break_counter = 0

    for element in element_link_list:
        element_url = element.get_attribute('href')
        if element_url in existing_file_links:
            continue
        existing_file_links.append(element_url)

        sleep(5)

        driver.execute_script("arguments[0].scrollIntoView();", element)
        ActionChains(driver).key_down(Keys.CONTROL).click(element).key_up(Keys.CONTROL).perform()
        driver.switch_to.window(driver.window_handles[1])

        element_download_button = None
        try:
            element = WebDriverWait(driver, 30).until(
                ec.presence_of_element_located((By.CLASS_NAME, "documentDownload"))
            )
            element_download_button = driver.find_element_by_class_name("documentDownload")

            req = requests.get(element_download_button.get_attribute("href"), allow_redirects=True)

            if req is not None and len(req.content) > 0:
                file_counter += 1
                no_break_counter += 1
                open(file_pdf_directory + "/" + str(file_counter + existing_file_count) + ".pdf", 'wb').write(req.content)
                file_size = len(req.content)
                total_file_size += file_size

                element_filename_container = driver.find_element_by_class_name("documentList")
                element_filename_label = element_filename_container.find_element_by_tag_name("h4")
                file_name = element_filename_label.text

                with open(file_id_path, "a", encoding='UTF-8') as file_object:
                    file_object.write(
                        str(file_counter + existing_file_count) + " " + file_name + " " + element_url + "\n")

                    log_activity(
                        current_datetime() + "\nFile count: " + str(file_counter) + "\nTotal size " + readable_size(
                            total_file_size))
        except (NoSuchElementException, TimeoutException) as E:
            log_activity(current_datetime() + " " + str(E.msg) + "\n" + str(E.stacktrace))
        finally:
            sleep(randint(5, 10))
            driver.close()
            driver.switch_to.window(driver.window_handles[0])

    page_counter = page_counter + 1
    log_activity(current_datetime() + "\nGoing to page {0}\n".format(page_counter))
    driver.get(pager_link + str(page_counter))
