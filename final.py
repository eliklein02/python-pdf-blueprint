import streamlit as st

from PyPDF2 import PdfReader, PdfWriter
from PyPDF2.generic import AnnotationBuilder, FloatObject

import random
import base64
import json
import concurrent.futures
from datetime import datetime
import os
import io


from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from webdriver_manager.chrome import ChromeDriverManager

from urllib.parse import quote
from urllib.parse import urlparse
import time
import requests

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload

try:
    SCOPES = ['https://www.googleapis.com/auth/drive']
    SERVICE_ACCOUNT = {
        "type": os.getenv("GOOGLE_CLOUD_TYPE"),
        "project_id": os.getenv("GOOGLE_CLOUD_PROJECT_ID"),
        "private_key_id": os.getenv("GOOGLE_CLOUD_PRIVATE_KEY_ID"),
        "private_key": os.getenv("GOOGLE_CLOUD_PRIVATE_KEY").replace("\\n", "\n"),
        "client_email": os.getenv("GOOGLE_CLOUD_CLIENT_EMAIL"),
        "client_id": os.getenv("GOOGLE_CLOUD_CLIENT_ID"),
        "auth_uri": os.getenv("GOOGLE_CLOUD_AUTH_URI"),
        "token_uri": os.getenv("GOOGLE_CLOUD_TOKEN_URI"),
        "auth_provider_x509_cert_url": os.getenv("GOOGLE_CLOUD_AUTH_PROVIDER_X509_CERT_URL"),
        "client_x509_cert_url": os.getenv("GOOGLE_CLOUD_CLIENT_X509_CERT_URL")
    }
    credentials = service_account.Credentials.from_service_account_info(
        SERVICE_ACCOUNT, scopes=SCOPES
    )
    service = build('drive', 'v3', credentials=credentials)
except Exception as e:
    st.error("Error finding credentials file. Please contact the developer.")

new_annots = []
annotation_count = 0
processed_annotations = 0

def pdf_iter(file):
    global annotation_count
    st.write("Starting process...")
    count = 0
    reader = PdfReader(file)
    writer = PdfWriter()
    annotations = []
    for i in range(len(reader.pages)):
        page = reader.pages[i]
        if "/Annots" in page:
            for a in page["/Annots"]:
                if count >= 17:
                    break
                link = a["/A"]["/URI"]
                rect = a["/Rect"]
                annot = {
                    "url": link,
                    "rect": rect,
                    "page": i
                }
                annotations.append(annot)
                count = count + 1
                annotation_count = len(annotations)
            st.write(f"Found {annotation_count} annotations.")
            del page["/Annots"]
            writer.add_page(page)
    today = datetime.today()
    day_name = today.strftime('%A')
    time = today.strftime('%I:%M %p')
    c = day_name + "-" + str(today).split(" ")[0] + "-" + time
    parent_folder = create_folder(c, "1JtiUFBlXchgibYyMVTBLmWqSrvrapptg")
    viewable_images_folder = create_folder("360 Images", parent_id=parent_folder)
    required_assets_folder = create_folder("required_assets", parent_id=viewable_images_folder)
    current_dir = os.getcwd()
    required_assets_folder_local = os.path.join(current_dir + "/required_assets")
    files_in_r_a = os.listdir(required_assets_folder_local)
    for a in files_in_r_a:
        if a.split(".")[1] == "css":
            mime_type = "text/css"
        else:
            mime_type = "text/javascript"
        upload_file(f"./required_assets/{a}", mime_type, folder_id=required_assets_folder)

    new = rate_limited(annotations, viewable_images_folder)

    for i in new:
        page = reader.pages[i[0]]
        rect = i[1]
        name = i[2]
        a = AnnotationBuilder.link(
            rect=(rect[0], rect[1], rect[2], rect[3]),
            url=name + ".html",
        )
        writer.add_annotation(page_number=i[0], annotation=a)
    

    with open("output.pdf", "wb") as output_pdf:
        writer.write(output_pdf)

    upload_file("./output.pdf", "application/pdf", folder_id=viewable_images_folder)

    os.remove("./output.pdf")
        
def rate_limited(array, folder, limit=5):
    to_return = []
    count = 0
    chunks = array[count:count + limit]
    print(f"Chunks: {chunks}")
    for i in range(0, len(array), limit):
        chunks = array[i:i + limit]
        with concurrent.futures.ProcessPoolExecutor() as e:
            new = list(e.map(process_annotation_wrapper, [(a, folder) for a in chunks]))
            to_return.extend(new)
    return to_return

def process_annotation_wrapper(args):
    a, folder = args
    print(f"Processing annotation: {a}, folder: {folder}")
    return process_annotation(a, folder)


def process_annotation(a, folder):
    try:
        link = a['url']
        rect = a['rect']
        page = a['page']
    except KeyError:
        link = a['url']
        rect = a['rect']
        page = a['page']
    payload = extract_googleapis_link(link)
    try:
        url = payload['url'][0]
        name = payload['name']
    except KeyError:
        payload = extract_googleapis_link(link)
        print(payload)
        url = payload['url'][0]
        name = payload['name']
    image_data = get_image_from_storage(url, link)
    process_img_data(image_data, name, folder)
    return [page, rect, name]

def extract_googleapis_link(url):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    service = Service(ChromeDriverManager().install())
    # service=Service("./chromedriver")
    caps = DesiredCapabilities.CHROME
    caps['goog:loggingPrefs'] = {'performance': 'ALL'}
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    driver = webdriver.Chrome(options=options, service=service)
    try:
        payload = {}
        count = 0
        while payload == {}:
            print(f"goign again {count + 1}")
            entries = get_url(url, driver=driver)
            payload = find_storage_url(entries)
            count +=1
    except Exception as e:
        print(e)
    finally:
        driver.quit()
    return payload

def get_url(url, driver):
        driver.get(url)
        entries = driver.get_log('performance')
        time.sleep(4)
        return entries

def find_storage_url(entries):
    payload = {}
    for entry in entries:
        message = json.loads(entry['message'])
        method = message['message']['method']
        if method == 'Network.requestWillBeSent':
            if message and message["message"] and message["message"]["params"] and message["message"]["params"]["request"] and message["message"]["params"]["request"]["url"]:
                url = message['message']['params']['request']['url']
            else:
                continue
            url_parsed = urlparse(url)
            if url_parsed.hostname == 'storage.googleapis.com':
                payload["url"] = url,
                payload["name"] = url.split("/")[5].split(".")[0]
                break
    return payload


def get_image_from_storage(img_url, ref):
    print(f"img_url: {img_url}")
    headers = {
        'Accept': 'image/*,*/*;q=0.9',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Origin': 'https://www.dronedeploy.com',
        'Pragma': 'no-cache',
        'Referer': ref,
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'cross-site',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
        'X-Client-Data': 'CJe2yQEIprbJAQipncoBCKaRywEIk6HLAQid/swBCIagzQEIkN/OARiPzs0B',
        'sec-ch-ua': '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"'
    }

    response = requests.get(img_url, headers=headers)
    return response._content

def process_img_data(img_data, name, folder):
        html_content = f"""
        <html>
        <head>
            <title>360 Image</title>
            <meta name="description" content="Display a single-resolution cubemap image." />
            <meta name="viewport" content="target-densitydpi=device-dpi, width=device-width, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0, user-scalable=no, minimal-ui" />
            <style>
            @-ms-viewport {{ width: device-width; }}
            </style>
            <link rel="stylesheet" href="./required_assets/reset.css">
            <link rel="stylesheet" href="./required_assets/style.css">
        </head>
        <body>
            <div id="pano"></div>
            <script src="./required_assets/es5-shim.js"></script>
            <script src="./required_assets/eventShim.js"></script>
            <script src="./required_assets/requestAnimationFrame.js" ></script>
            <script src="./required_assets/marzipano.js" ></script>
            <script>
                var img_data = "data:image/jpeg;base64,{base64.b64encode(img_data).decode('utf-8')}";
            </script>
            <script src="./required_assets/index.js"></script>
        </body>
        </html>
        """
        name = f"{name}.html"
        file = io.BytesIO(html_content.encode('utf-8'))
        res = html_file_upload(file, name, folder)
def create_folder(name, parent_id=None):
    folder_metadata = {
        "name": name,
        'mimeType': 'application/vnd.google-apps.folder'
    }

    if parent_id:
        folder_metadata["parents"] = [parent_id]

    try:
        folder = service.files().create(body=folder_metadata, fields="id").execute()
    except Exception as e:
        st.write("Error:")
        st.write(e)
        st.write("Please try again.")
        return
    return folder.get("id")

def upload_file(file_path, mime_type, folder_id=None):
    name = file_path.split("/")[-1]
    file_metadata = { "name": name }
    if folder_id:
        file_metadata["parents"] = [folder_id]

    try:
        media = MediaFileUpload(file_path, mimetype=mime_type)
        file = service.files().create(body = file_metadata, media_body = media, fields = "id", ).execute()
    except Exception as e:
        st.write("Error:")
        st.write(e)
        st.write("Please try again.")
        return
    return file

def html_file_upload(file, name, folder):
    print(file)
    print(name)
    file_metadata = {
        "name": name,
        "parents": [folder]
    }

    media = MediaIoBaseUpload(file, mimetype="text/html", resumable=True)
    file = service.files().create(body=file_metadata, media_body=media, fields="id").execute()
    return file

uploaded = st.file_uploader("Please upload a pdf")

if uploaded is not None:
    button = st.button("Start")
    if button:
        random_number = random.randint(100, 1000000)
        random_number = str(random_number)
        bytes_data = uploaded.getvalue()
        file_name = uploaded.name.split(".")[0]
        file_extension = uploaded.name.split(".")[1]
        try:
            pdf_iter(file_name + "." + file_extension)
        except Exception as e:
            st.write("Error:")
            st.write(e)
            st.write("Please try again.")