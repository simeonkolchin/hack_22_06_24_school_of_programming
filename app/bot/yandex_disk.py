import requests
import os

YANDEX_DISK_TOKEN = 'y0_AgAAAAA_HVueAAwL5gAAAAEJTfaWAAA4Yozwwv1OPr-DuTuqqpLD9lvQQw'

def upload_to_yandex_disk(file_path, national_project, region, object_type, address):
    headers = {
        'Authorization': f'OAuth {YANDEX_DISK_TOKEN}'
    }
    disk_path = f"/branding_photos/{national_project}/{region}/{object_type}/{address}/{os.path.basename(file_path)}"
    upload_url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
    params = {'path': disk_path, 'overwrite': 'true'}
    response = requests.get(upload_url, headers=headers, params=params)
    upload_link = response.json().get('href')
    with open(file_path, 'rb') as f:
        requests.put(upload_link, files={'file': f})

    return f"https://disk.yandex.com/client/disk{disk_path}"
