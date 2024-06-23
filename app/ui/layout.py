import streamlit as st
from PIL import Image
from utils.utils import preprocess_image
from ml.classification_direction import ImageClassifierONNX

def render_layout(models):
    st.title("Image Prediction App")

    uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
    option1 = st.selectbox("Select Option 1", ["Option 1A", "Option 1B", "Option 1C"])
    option2 = st.selectbox("Select Option 2", ["Option 2A", "Option 2B", "Option 2C"])

    selected_model = st.selectbox("Select Model", list(models.keys()))

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption='Uploaded Image', use_column_width=True)
        
        if st.button("Predict"):
            model = models[selected_model]
            processed_image = preprocess_image(image)
            result = model(processed_image)
            st.write("Prediction result:", result)
