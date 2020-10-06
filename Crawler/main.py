from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from time import sleep
import requests

profile = webdriver.FirefoxProfile()
profile.set_preference("browser.download.folderList", 2)
profile.set_preference("browser.download.manager.showWhenStarting", False)
profile.set_preference("browser.download.dir", "D:/Rozsudky")
#profile.set_preference("browser.download.useDownloadDir", True)
#profile.set_preference("pdfjs.disabled", True)
#profile.set_preference('browser.helperApps.neverAsk.openFile', True)
#profile.set_preference("privacy.cpd.downloads", False)
profile.set_preference("browser.helperapps.neverAsk.saveToDisk", "application/octet-stream,application/pdf")
driver = webdriver.Firefox(firefox_profile=profile)

driver.get("https://obcan.justice.sk/infosud/-/infosud/zoznam/rozhodnutie")


element_file_list_container = driver.find_element_by_id("_isufront_WAR_isufront_mapsSearchContainer")
element_link_list = element_file_list_container.find_elements_by_tag_name("a")

i = 0
for element in element_link_list:
    sleep(5)
    driver.execute_script("arguments[0].scrollIntoView();", element)
    ActionChains(driver).key_down(Keys.CONTROL).click(element).key_up(Keys.CONTROL).perform()
    driver.switch_to.window(driver.window_handles[1])
    sleep(5)
    element_download_button = driver.find_element_by_class_name("documentDownload")
    #element_download_button.click()

    req = requests.get(element_download_button.get_attribute("href"), allow_redirects=True)
    open("D:/Rozsudky/File"+str(i)+".pdf", 'wb').write(req.content)
    i += 1
    print("Downloaded file")

    sleep(30)
    driver.close()
    driver.switch_to.window(driver.window_handles[0])

#D:\Rozsudky
#element = driver.find_element_by_id("email")