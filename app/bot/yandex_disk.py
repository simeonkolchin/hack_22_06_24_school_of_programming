import yadisk
import os

YANDEX_DISK_TOKEN = 'y0_AgAEA7qkdfRMAAwMEQAAAAEJVAvkAABBm8lrXWZIsbhqMs0yZApmIwrKUA'

# Инициализация Yandex Disk клиента
y = yadisk.YaDisk(token=YANDEX_DISK_TOKEN)

def upload_to_yandex_disk(file_path, national_project, region, object_type, address):
    # Определение пути на Яндекс.Диске
    disk_path = f"/branding_photos/{national_project}/{region}/{object_type}/{address}"
    
    # Создание необходимых директорий, если их нет
    if not y.exists(disk_path):
        if not y.exists(f"/branding_photos/{national_project}"):
          y.mkdir(f"/branding_photos/{national_project}")
        if not y.exists(f"/branding_photos/{national_project}/{region}"):
          y.mkdir(f"/branding_photos/{national_project}/{region}")
        if not y.exists(f"/branding_photos/{national_project}/{region}/{object_type}"):
          y.mkdir(f"/branding_photos/{national_project}/{region}/{object_type}")
        y.mkdir(disk_path)
    
    # Определение полного пути для файла на Яндекс.Диске
    full_disk_path = f"{disk_path}/{os.path.basename(file_path)}"
    
    # Загрузка файла на Яндекс.Диск
    with open(file_path, 'rb') as f:
        y.upload(f, full_disk_path, overwrite=True)
    
    # Возвращаем URL загруженного файла
    return f"https://disk.yandex.com/client/disk{full_disk_path}"
