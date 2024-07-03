import yadisk
import os

YANDEX_DISK_TOKEN = 'y0_AgAAAAA_HVueAAwMEQAAAAEJUr26AADq10NchJxAGYiWumEZJHC1TixtRw'

# Инициализация Yandex Disk клиента
y = yadisk.YaDisk(token=YANDEX_DISK_TOKEN)

def upload_to_yandex_disk(file_path, national_project, region, object_type, address):
    # Определение пути на Яндекс.Диске
    disk_path = f"/branding_photos/{national_project}/{region}/{object_type}/{address}/{os.path.basename(file_path)}"
    
    # Загрузка файла на Яндекс.Диск
    with open(file_path, 'rb') as f:
        y.upload(f, disk_path, overwrite=True)
    
    # Возвращаем URL загруженного файла
    return f"https://disk.yandex.com/client/disk{disk_path}"

