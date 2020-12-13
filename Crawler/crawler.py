####################################################################################################################
# This script is the CRAWLER. Can be run from windows cmd (or from IDE). Will crawl the obcan.justice.sk site ######
# and download pdf files. Does not require human input.                                                       ######
####################################################################################################################

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait
from time import sleep
from random import randint, random
from datetime import datetime
import requests

from os.path import exists, isfile, join
from os import listdir, getcwd
import sys

# Mandatory if we want to run this scripts from windows cmd. Must precede all imports from this project
conf_path = getcwd()
sys.path.append(conf_path)
sys.path.append(conf_path + '..')
sys.path.append(conf_path + '../..')

# Custom imports from other folders of this project
# All paths to directories within project are held in one play, to be able to change them easily.
from shared_info import file_pdf_directory, file_id_path


# https://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size
# Very simple function to convert file size from bytes to human-readable string. Convenient for console output
def readable_size(num, suffix='B'):
    for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


# Simple way to get current time in unified format
def current_datetime():
    now = datetime.now()
    return now.strftime("%d-%m-%Y %H-%M-%S")


# We save the current time to be able to tell the user how long current crawling session lasts
start_datetime = current_datetime()


# Unified way to log crawler activity. Useful for later debugging
def log_activity(message):
    print(message)
    log_file_object = open("./Log/activity_log_" + start_datetime + ".txt", "a+")
    log_file_object.write(message)
    log_file_object.close()


# Link to connect to. Modified to use maximum paging. Current page number needs to be appended to end of this strings
pager_link = "https://obcan.justice.sk/infosud?p_p_id=isufront_WAR_isufront&p_p_col_id=column-1&p_p_col_count=1&p_p_mode=view&_isufront_WAR_isufront_view=list&p_p_state=normal&_isufront_WAR_isufront_entityType=rozhodnutie&_isufront_WAR_isufront_delta=75&_isufront_WAR_isufront_cur="

# Selenium webdriver configuration. We are using Firefox, it has proven to be more convenient.
profile = webdriver.FirefoxProfile()
profile.set_preference("browser.download.folderList", 2)
profile.set_preference("browser.download.manager.showWhenStarting", False)
profile.set_preference("browser.download.dir", file_pdf_directory)
profile.set_preference("browser.helperapps.neverAsk.saveToDisk", "application/octet-stream,application/pdf")
driver = webdriver.Firefox(firefox_profile=profile)

# Initialize progress counters.
page_counter = 1        # Pagination counter. How many pages (of size 75) have already been visited + 1 => Current page
file_counter = 0        # File counter. How many files have been downloaded in this session.
total_file_size = 0     # Total size of all downloaded files in this session.
no_break_counter = 0    # How many files have been downloaded in this session without taking a human-like break for cca 10 minutes

# Initialize array of links to files that were donwloaded in previous sessions. This is to prevent duplicit downloading
existing_file_links = []
if exists(file_id_path):
    with open(file_id_path, "r", encoding='UTF-8') as file_object:
        for line in file_object:
            link = line.replace('\n', '').split(' ')[2]
            existing_file_links.append(link)

# Let's determine how many files have been downloaded in total in previous sessions for console output purposes
all_existing_id_list = [int(f.replace('.pdf', '')) for f in listdir(file_pdf_directory) if isfile(join(file_pdf_directory, f))]
existing_file_count = max(all_existing_id_list)
# Let's output the result
print(str(existing_file_count) + " files exists")
# Let's log starting session
log_activity(current_datetime() + "\nHas {0} files\n".format(existing_file_count))
log_activity(current_datetime() + "\nStarting crawling session\n")

# Let's load the desired web site
driver.get(pager_link + str(page_counter))

print('Proceeding to crawling')

# Loop infinitely through pages of website. Each page has 75 documents. This won't stop until unhandled exception occurs
# or script is stopped.
while True:
    # Give the page time load and try to prevent being too greedy for the site's server.
    sleep(15)

    # Let's find all buttons for documents. They can be found within precisely defined container
    # Only "a" elements in that container are document info buttons, so no need to be more specific
    element_file_list_container = driver.find_element_by_id("_isufront_WAR_isufront_mapsSearchContainer")
    element_link_list = element_file_list_container.find_elements_by_tag_name("a")

    # Let's take a break for 5-10 minutes every 200 or so documents, so crawler might appear more like a regular user
    # Usefulness of this feature may be questionable, but why take a chance?
    if (random() < 0.03 and no_break_counter > 50) or no_break_counter > 200:
        break_time = randint(300, 600)
        log_activity(current_datetime() + " Taking a human-like break for %d seconds\n" % break_time)
        sleep(break_time)
        log_activity(current_datetime() + " Back to work\n")
        no_break_counter = 0

    # Loop over all documents on current page. For each document, let's see if we already have it and if not,
    # let's download it
    for element in element_link_list:
        # Get URL which is reffered to by current button.
        element_url = element.get_attribute('href')
        # If we have already downloaded from this URL, let's skip it.
        if element_url in existing_file_links:
            continue
        # This is a new URL, so we'll download from it. Let's save it into (transient) list of existing URLs,
        # in case we encounter it in this session again (unlikely)
        existing_file_links.append(element_url)

        # Sleep for a little while, si that we are not too greedy
        sleep(5)

        # Now we need to press the button leading to page with detail of a document.
        # To do that, we first need to scroll onto it
        # (Selenium does not allow clicking on elements that are not on screen)
        driver.execute_script("arguments[0].scrollIntoView();", element)
        # We want to open the page in new card, so that the current page does not need to refreshed when we return.
        # To do that, we simulate combo CTRL + LEFT CLICK
        ActionChains(driver).key_down(Keys.CONTROL).click(element).key_up(Keys.CONTROL).perform()
        # Now let's switch to the new card
        driver.switch_to.window(driver.window_handles[1])

        # We are on details page of a document. Let's find the download button and download the file.
        # If we fail, no big deal, let's just skip this file and carry on. Shit happens.
        element_download_button = None
        try:
            # Let's try to locate the download button. Give it some time, as the page loading may take a moment.
            # In some cases, the button may not be there - know to happen about twice
            # If it is not found until the timeout, exception will be thrown and handled in 'catch' block below
            element = WebDriverWait(driver, 30).until(
                ec.presence_of_element_located((By.CLASS_NAME, "documentDownload"))
            )
            element_download_button = driver.find_element_by_class_name("documentDownload")

            # We wanted to click download button, however by default a popup shows up asking for action (Download/Open)
            # This cannot be handled via Selenium and workarounds failed.
            # Instead, we get the download link a send raw GET request via Requests library.

            # Let's get the download link from the button and send GET requests. Very simple thanks to the library.
            req = requests.get(element_download_button.get_attribute("href"), allow_redirects=True)

            # If the download link is non-empty (or exists at all), proceed to downloading
            if req is not None and len(req.content) > 0:
                # Increment the session progress counters
                file_counter += 1
                no_break_counter += 1
                # Write the obtained file content on disk.
                open(file_pdf_directory + "/" + str(file_counter + existing_file_count) + ".pdf", 'wb').write(req.content)
                # Increment session total download size counter
                file_size = len(req.content)
                total_file_size += file_size

                # Obtain name of pdf file to be used in console output.
                element_filename_container = driver.find_element_by_class_name("documentList")
                element_filename_label = element_filename_container.find_element_by_tag_name("h4")
                file_name = element_filename_label.text

                # Let's mark the downloaded file persistently - we will be able to translate between its custom id
                # and download link.
                with open(file_id_path, "a", encoding='UTF-8') as file_object:
                    file_object.write(
                        str(file_counter + existing_file_count) + " " + file_name + " " + element_url + "\n")
                    # Log crawler activity into current session log file
                    log_activity(
                        current_datetime() + "\nFile count: " + str(file_counter) + "\nTotal size " + readable_size(
                            total_file_size))
        # If exception (of expected type) occured during donwloading, log it and keep moving
        except (NoSuchElementException, TimeoutException) as E:
            log_activity(current_datetime() + " " + str(E.msg) + "\n" + str(E.stacktrace))
        # Whether downloading the document was successful or not, we wait for a moment to prevent from being greedy,
        # close current card and return to page with offered 75 documents
        finally:
            sleep(randint(5, 10))
            driver.close()
            driver.switch_to.window(driver.window_handles[0])

    # We have looped over all documents on current page, so we increase page counter,
    # log this event and navigate to next page
    page_counter = page_counter + 1
    log_activity(current_datetime() + "\nGoing to page {0}\n".format(page_counter))
    driver.get(pager_link + str(page_counter))
