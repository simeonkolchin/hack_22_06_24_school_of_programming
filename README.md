# Logo Error Checker Project

Проект Logo Error Checker представляет собой систему для обнаружения и классификации ошибок в логотипах на изображениях. Система использует различные модели машинного обучения для анализа изображений, распознавания текста, поиска людей и проверки цвета.

## Идея проекта

Цель проекта - создать инструмент, который поможет пользователям автоматически проверять изображения на наличие логотипов и их правильное размещение, а также выявлять различные ошибки, такие как неправильное направление логотипов, наличие людей на изображении и т.д.

## Структура проекта

### `app/`

Директория `app` содержит весь исходный код для запуска и работы проекта, включая API, Telegram-бота, машинное обучение и пользовательский интерфейс.

- `api/`

  - `__init__.py`
  - `api.py`: Реализация FastAPI для взаимодействия с внешними приложениями.

- `bot/`

  - `__init__.py`
  - `telegram_bot.py`: Код для Telegram-бота, использующего aiogram для обработки сообщений и взаимодействия с пользователями.

- `ml/`

  - `__init__.py`
  - `weights/`: Директория, содержащая веса моделей.
  - `classification_crop.py`: Модель классификации изображений.
  - `classification_direction.py`: Модель классификации направлений.
  - `color_checker.py`: Модель проверки цвета.
  - `logo_detector.py`: Модель обнаружения логотипов.
  - `ml.py`: Основной файл для интеграции всех моделей и проверок.
  - `ocr.py`: Модель распознавания текста.
  - `search_people.py`: Модель поиска людей на изображениях.

- `ui/`

  - `__init__.py`
  - `layout.py`: Код для Streamlit-приложения, позволяющего загружать изображения и получать результаты классификации.

- `utils/`

  - `__init__.py`
  - `utils.py`: Вспомогательные функции и утилиты для проекта.

- `main.py`: Основной файл для запуска Streamlit-приложения, Telegram-бота и API.

### `data/`

Директория `data` содержит все фотографии, используемые для обучения и тестирования моделей.

#### Структура

- `classification_crop/`: Изображения для обучения и тестирования модели классификации изображений.
- `classification_direction/`: Изображения для обучения и тестирования модели классификации направлений.
- `direction/`: Дополнительные изображения для классификации направлений.
- `detection_all/`: Изображения для обнаружения всех объектов.
- `original/`: Оригинальные изображения для различных задач классификации и обнаружения.

### `train/`

Директория `train` содержит Jupyter ноутбуки, используемые для подбора весов моделей и их обучения.

#### Структура

- `classification_crop/`
  - `train.ipynb`: Ноутбук для обучения модели классификации изображений.
- `classification_direction/`
  - `1.ipynb`: Ноутбук для обучения модели классификации направлений.
- `ocr/`
  - `ocr.ipynb`: Ноутбук для обучения модели распознавания текста.
- `znak_detection/`
  - `yolo_detection.ipynb`: Ноутбук для обучения модели обнаружения логотипов.

## Установка

1. Клонируйте репозиторий:

```bash
git clone https://github.com/simeonkolchin/hack_22_06_24_school_of_programming
cd logo-error-checker
```

2. Установите необходимые библиотеки:

```bash
pip install -r requirements.txt
```

## Запуск проекта

Для запуска проекта выполните одну/все команду(ы) из корневой директории:

Запуск телеграм-бота:

```bash
set PYTHONPATH=%cd%
python app\bot\telegram_bot.py
```

Запуск приложения streamlit:

```bash
streamlit run app/ui/layout.py
```

# Использование API

## Базовый URL

```arduino
http://<your_server_ip>:8000
```

## Эндпоинты

Проверка ошибок на изображении

```bash
POST /check_errors/
```

Описание: Загружает изображение и возвращает список обнаруженных ошибок.

Параметры запроса:

- file: Файл изображения (обязательный параметр).

## Пример запроса:

```http
POST /check_errors/ HTTP/1.1
Host: <your_server_ip>:8000
Content-Type: multipart/form-data
Content-Length: <length>
Content-Disposition: form-data; name="file"; filename="example.jpg"
```

## Пример ответа:

```json
{
  "errors": [
    "Logo classification error: low confidence score.",
    "OCR error: Text not found",
    "YOLO detection error: no objects detected.",
    "Person detection error: no persons detected."
  ]
}
```

# Примеры использования

## Python

```python
import requests

url = "http://<your_server_ip>:8000/check_errors/"
file_path = "path_to_your_image.jpg"

with open(file_path, "rb") as image_file:
    files = {"file": image_file}
    response = requests.post(url, files=files)

if response.status_code == 200:
    print("Errors detected:", response.json().get("errors"))
else:
    print("Failed to check errors:", response.status_code)
```

## cURL

```cURL
curl -X POST "http://<your_server_ip>:8000/check_errors/" -F "file=@path_to_your_image.jpg"
```

## JavaScript (Fetch API)

```javascript
async function checkErrors(imageFile) {
  const url = 'http://<your_server_ip>:8000/check_errors/';
  const formData = new FormData();
  formData.append('file', imageFile);

  const response = await fetch(url, {
    method: 'POST',
    body: formData,
  });

  if (response.ok) {
    const data = await response.json();
    console.log('Errors detected:', data.errors);
  } else {
    console.error('Failed to check errors:', response.status);
  }
}

// Пример использования
const imageFile = document.querySelector('input[type="file"]').files[0];
checkErrors(imageFile);
```

## Контакты

Если у вас возникли вопросы или предложения, вы можете связаться с нами по электронной почте [simeonkolchin@gmail.com].
