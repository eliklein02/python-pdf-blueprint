# import streamlit as st
# from PyPDF2 import PdfReader, PdfWriter
# from PyPDF2.generic import DictionaryObject, ArrayObject, IndirectObject
# import random
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
# from urllib.parse import quote
# from urllib.parse import urlparse
# import time
# import requests
# from google.oauth2 import service_account
# from googleapiclient.discovery import build
# from googleapiclient.http import MediaFileUpload
# import base64
# import json
# import concurrent.futures
# from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


# def extract_googleapis_link(url):
#     options = webdriver.ChromeOptions()
#     service = Service(ChromeDriverManager().install())
#     caps = DesiredCapabilities.CHROME
#     caps['goog:loggingPrefs'] = {'performance': 'ALL'}
#     options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
#     driver = webdriver.Chrome(options=options, service=service)
#     try: 
#         entries = get_url(url, driver=driver)
#         payload = find_storage_url(entries)

#         if payload == []:
#             print("going again")
#             entries = get_url(url, driver=driver)
#             payload = find_storage_url(entries)
#         else:
#             driver.quit()
#     except Exception as e:
#         print(e)
#     return payload

# def get_url(url, driver):
#         driver.get(url)
#         entries = driver.get_log('performance')
#         time.sleep(2)
#         return entries

# def find_storage_url(entries):
#     payload = []
#     for entry in entries:
#         message = json.loads(entry['message'])
#         method = message['message']['method']
#         if method == 'Network.requestWillBeSent':
#             url = message['message']['params']['request']['url']
#             url_parsed = urlparse(url)
#             if url_parsed.hostname == 'storage.googleapis.com':
#                 image = {
#                     "url": url,
#                     "name": url.split("/")[5].split(".")[0]
#                 }
#                 payload.append(image)
#                 break
#     return payload

# p = extract_googleapis_link("https://www.dronedeploy.com/app2/sites/667f19762172612132175cf2/preprocessed-pano/667f198121726121321764ab/assets/667f19892172612132176ff7?jwt_token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpZCI6IjY2N2YxOTgwMjE3MjYxMjEzMjE3NjNlZCIsInR5cGUiOiJQdWJsaWNTaGFyZVYyIiwiYWNjZXNzX3R5cGUiOiJzaW5nbGVNZWRpYSIsImFzc2V0X2lkIjoiNjY3ZjE5ODkyMTcyNjEyMTMyMTc2ZmY3In0.nfl5mRkkSwIP-SprRrfC2jMvC6FTa163WbR3whQRWT5amLXfhGtJgsWc7WXppmiyzEtL38mrU1ZKW5FajPvrJA")