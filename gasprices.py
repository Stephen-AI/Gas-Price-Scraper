from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import StaleElementReferenceException
import requests
import os
import json
import tablib
from datetime import datetime

# class Price:
#     def __init__(self, price, datetime):
#         self.value = price
#         self.time = datetime

#     def default(self): # pylint: disable=E0202
#         return {
#             "date time":self.time,
#             "price":self.value
#         }

class Address:
    def __init__(self, addr, price):
        self.name = addr
        self.price = price

    def default(self): # pylint: disable=E0202
        return {
            "address":self.name,
            "price":self.price
        }


class Station:
    def __init__(self, name):
        self.name = name
        self.addresses = {}

    def add_address(self, addr):
        if addr.name not in self.addresses:
            self.addresses[addr.name] = addr

    def default(self): # pylint: disable=E0202
        return {
            "station":self.name,
            "addresses":list([addr.default() for addr in self.addresses.values()])
        }


def add_pluses(strng):
    return '+'.join(strng.split())

def createDriver():
    capability = DesiredCapabilities.CHROME.copy()
    driver = None
    capability['platform'] = "WINDOWS"
    capability['version'] = 10
    try:
        driver = webdriver.Chrome(executable_path="C:/Users/saigbomian/Downloads/chromedriver_win32/chromedriver.exe", port=9515)
    except Exception as e:
        print(e)
    return driver

def export(time, prices, tojson=False):
    jsn = {}
    data = []
    time = time.split()
    t = [time[0]] + time[1].split(":")
    file_name = "{} {};{};{}.json".format(*t)
    for v in prices.values():
        data.append(v.default())
    jsn['stations'] =  data
    if tojson:
        with open(file_name, 'w+') as fi:
            json.dump(jsn,fi, indent=True)
    return jsn

    toexcel(time, prices, file_name=file_name)
    print("{} created".format(file_name))

def toexcel(time, prices, file_name=None):
    data = 1
    with open(file_name) as fi:
        data = tablib.Dataset().load(fi.read())
    data.export('xls')
    print(data)



def retryClick(driver, selector):
    attempts = 0
    working = False
    while attempts < 5 and not working:
        try:
            print("Failed to click button, executing attempt {}".format(attempts+1))
            driver.find_element_by_css_selector(selector)
            working = True
        except StaleElementReferenceException:
            pass
        attempts += 1
    return working

def retry(driver, search, type, var):
    attempts = 0
    val = None
    attr = 'innerHTML'
    while attempts < 10 and not val:
        try:
            print("Failed to get {}, executing attempt {}".format(var, attempts+1))
            if type == 'css':
                val = driver.find_element_by_css_selector(search).get_attribute(attr)
            elif type == 'class':
                val = driver.find_element_by_class_name(search).get_attribute(attr)
            elif type == 'id':
                val = driver.find_element_by_id(search).get_attribute(attr)
        except StaleElementReferenceException:
            pass
        attempts += 1
    return val


def get_current_prices(driver, getjson=False, location="me", num_stations=40):
    time = str(datetime.today().replace(microsecond=0))
    price_selector = "section-result-regular-gas-price" #The class for the price of the gas
    header_class = "section-result-text-content" #Each gas station result on the page has this class name
    next_button_selector = "span.section-pagination-button-next" #next button. Each page has 20 stations
    address_selector = "span.section-result-location" #CSS Selector for the address
    encoded_location = add_pluses(location)
    url = "https://www.google.com/maps/search/?api=1&query=gas+stations+near+{}".format(encoded_location)
    driver.get(url)
    prices = {}
    count = 0

    while count < num_stations:
        list_of_stations = driver.find_elements_by_class_name(header_class)
        for station in list_of_stations:
            try:
                stat = station.find_element_by_css_selector('h3.section-result-title span').get_attribute('innerHTML')
            except StaleElementReferenceException:
                stat = retry(station, 'h3.section-result-title span',"css", "station")
            try:
                addr = station.find_element_by_css_selector(address_selector).get_attribute('innerHTML')
            except StaleElementReferenceException:
                addr = retry(station, address_selector, "css", "address")
            try:
                price = station.find_element_by_class_name(price_selector).get_attribute('innerHTML')
            except StaleElementReferenceException:
                price = retry(station, price_selector, "class", "price")
            new_address = Address(addr, price)
            if stat not in prices:
                prices[stat] = Station(stat)
            prices[stat].add_address(new_address)
        count += len(list_of_stations)
        try:
            driver.find_element_by_css_selector(next_button_selector).click()
        except Exception:
            retryClick(driver, next_button_selector)

    export(time,prices, tojson=getjson)

# get_current_prices(createDriver())

