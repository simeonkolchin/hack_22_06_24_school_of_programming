import streamlit as st
from PIL import Image
import tracemalloc
import sys
import os
import io

# Включаем tracemalloc для отслеживания распределения памяти
tracemalloc.start()

# Добавляем корневую директорию в системный путь
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, os.pardir, os.pardir))
sys.path.append(project_root)

from app.ml.ml import LogoErrorChecker

def main():
    st.title('Image Classification with ONNX Model')
    st.write('Upload an image to classify it using the ONNX model.')

    # Загрузка изображения
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "png", "jpeg"])

    if uploaded_file is not None:
        # Преобразование загруженного файла в байтовый поток
        image = Image.open(uploaded_file).convert('RGB')
        st.image(image, caption='Uploaded Image.', use_column_width=True)
        st.write("Classifying...")

        # Инициализация класса проверки ошибок
        checker = LogoErrorChecker()

        # Предсказание
        error_list = checker.check_errors(image)
        if error_list:
            for error in error_list:
                st.write(f"Detected error: {error}")
        else:
            st.write("No errors detected.")

if __name__ == "__main__":
    main()
