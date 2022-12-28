import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="Home",
    page_icon="") 

#image_path = '\Users\Giovanna_Aleixo\Documents\data_science\dataset\food_delivery.jpg'
image_path = 'food_delivery.jpg'
image = Image.open('food_delivery.jpg')
st.sidebar.image(image, width = 300)

st.sidebar.markdown('# Curry Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")

st.write("# Curry Company Growth Dashboard")
st.markdown("# Texto explicativo")
