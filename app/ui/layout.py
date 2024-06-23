import streamlit as st
from PIL import Image
from ml.ml import LogoErrorChecker

def main():
    st.title('Image Classification with ONNX Model')
    st.write('Upload an image to classify it using the ONNX model.')

    # Загрузка изображения
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "png", "jpeg"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file).convert('RGB')
        st.image(image, caption='Uploaded Image.', use_column_width=True)
        st.write("Classifying...")

        # Инициализация класса проверки ошибок
        checker = LogoErrorChecker()

        # Предсказание
        error_list = checker.check_errors(uploaded_file)
        if error_list:
            for error in error_list:
                st.write(f"Detected error: {error}")
        else:
            st.write("No errors detected.")
