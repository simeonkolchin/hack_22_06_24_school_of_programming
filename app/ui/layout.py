import streamlit as st
from PIL import Image, ImageDraw, ImageOps
import tracemalloc
import sys
import os
import io
import tempfile

# Настройка страницы
st.set_page_config(page_title="Logo Checker", layout="wide")

# CSS стили для улучшения визуального оформления
st.markdown("""
    <style>
        .uploaded-image {
            max-width: 300px;
            max-height: 300px;
            margin-bottom: 20px;
        }
    </style>
""", unsafe_allow_html=True)

# Включаем tracemalloc для отслеживания распределения памяти
tracemalloc.start()

# Добавляем корневую директорию в системный путь
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, os.pardir, os.pardir))
sys.path.append(project_root)

from app.ml.ml import LogoErrorChecker

def main():
    # Боковая панель с логотипом, названием, описанием и инструкциями
    st.sidebar.image('app/ui/logo.png', use_column_width=True)
    st.sidebar.title("Logo Checker")

    st.sidebar.markdown("""
        ### Описание проекта
        **Logo Checker** - это инструмент для проверки изображений на наличие логотипов и их ошибок в брендировании национальных проектов. Система использует различные модели машинного обучения для анализа изображений, распознавания текста, поиска людей и проверки цвета.

        ### Цель проекта
        Цель проекта - создать инструмент, который поможет автоматически проверять изображения на соответствие требованиям брендирования национальных проектов. Это позволит существенно сократить время, затрачиваемое на ручную проверку изображений, и повысить точность проверки.

        ### Инструкции
        1. Загрузите изображение, которое хотите проверить.
        2. Нажмите кнопку "Классифицировать".
        3. Получите результаты и проверьте изображение на наличие ошибок.
                        
        ### Telegram Bot
        Вы также можете использовать нашего Telegram-бота для проверки изображений. [Перейти к боту](https://t.me/logo_checker_hack_bot)
        
        ### Подключение API
        Вы можете использовать наш API для интеграции с другими проектами. Ниже приведен пример использования API.
        
        ```python
        import requests

        url = 'http://your_api_endpoint'
        files = {'file': open('path_to_your_image.jpg', 'rb')}
        response = requests.post(url, files=files)
        print(response.json())
        ```
    """)

    # Основной интерфейс
    st.title('Классификация изображений с помощью модели ONNX')
    st.write('Загрузите изображение для классификации с использованием модели ONNX.')

    uploaded_file = st.file_uploader("Выберите изображение...", type=["jpg", "png", "jpeg"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file).convert('RGB')
        st.image(image, caption='Загруженное изображение.', use_column_width=False, width=300)
        st.write("Классификация...")

        checker = LogoErrorChecker()

        result = checker.check_errors(image)

        draw = ImageDraw.Draw(image)
        for bbox_result in result['bbox_results']:
            bbox = bbox_result['bbox']
            if isinstance(bbox, (list, tuple)) and len(bbox) >= 4:
                bbox = tuple(map(int, bbox[:4]))
                draw.rectangle(bbox, outline="red", width=2)

        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            image.save(tmp_file, format='PNG')
            tmp_file_path = tmp_file.name

        st.image(image, caption='Изображение с отмеченными логотипами.', use_column_width=False, width=300)

        caption = "### Распознанные ошибки:\n"
        for idx, bbox_result in enumerate(result['bbox_results']):
            caption += f"**Логотип {idx + 1}:**\n"
            caption += f"- **Координаты:** {bbox_result['bbox']}\n"
            caption += f"- **Класс:** {bbox_result['cropped_class']}\n"
            caption += f"- **Ошибки:** {', '.join(bbox_result['errors']) if bbox_result['errors'] else 'Нет'}\n"
            caption += f"- **OCR:** {bbox_result['ocr_class']}\n"
            caption += f"- **Цвет:** {bbox_result['color_class']}\n\n"
        caption += f"**OCR класс для всего изображения:** {result['ocr_class']}"

        st.markdown(caption)

if __name__ == "__main__":
    main()
