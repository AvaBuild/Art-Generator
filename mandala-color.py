import streamlit as st
import os
import io
import base64
from PIL import Image
from openai import OpenAI
import requests

# Set page config
st.set_page_config(page_title="Mandala Art Generator", page_icon="🎨", layout="centered")

# App title and description
st.title("✨ Mandala Art Generator ✨")
st.markdown("Create beautiful mandala art using AI with just a word of inspiration and your favorite color!")

# User inputs
with st.form("mandala_form"):
    # Inspiration word
    inspiration = st.text_input("Enter a word for inspiration:", placeholder="forest, ocean, galaxy, etc.")
    
    # Favorite color
    color = st.color_picker("Choose your favorite color:", "#FF5733")
    
    # Display the selected color name
    color_name = color.upper()
    st.write(f"Selected color: {color_name}")
    
    # API Key input with password masking
    api_key = st.text_input("Enter your OpenAI API Key:", type="password", help="Your API key will not be stored")
    
    # Submit button
    submitted = st.form_submit_button("Generate Mandala")

# Function to generate image
def generate_mandala(inspiration, color):
    # Format the color as a name (removing the # and converting to hex name)
    color_hex = color.lstrip('#')
    
    # Create the prompt for DALL-E
    prompt = f"Create a beautiful, symmetrical mandala inspired by '{inspiration}'. Use black, white, and {color_hex} as the primary colors. The design should be intricate, detailed, and suitable for printing. Make it centered and balanced with clear patterns."
    
    client = OpenAI(api_key=api_key)
    
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        
        # Get the image URL
        image_url = response.data[0].url
        
        # Download the image
        image_response = requests.get(image_url)
        image = Image.open(io.BytesIO(image_response.content))
        
        return image, image_url
    
    except Exception as e:
        st.error(f"Error generating image: {str(e)}")
        return None, None

# Generate image when form is submitted
if submitted:
    if not inspiration:
        st.error("Please enter an inspiration word.")
    elif not api_key:
        st.error("Please enter your OpenAI API key.")
    else:
        with st.spinner("Generating your mandala... This may take a moment."):
            image, image_url = generate_mandala(inspiration, color)
            
            if image:
                # Display the generated image
                st.success("✅ Your mandala has been generated!")
                st.image(image, caption=f"Mandala inspired by '{inspiration}'", use_column_width=True)
                
                # Convert PIL image to bytes for download
                buf = io.BytesIO()
                image.save(buf, format="PNG")
                byte_im = buf.getvalue()
                
                # Download button
                st.download_button(
                    label="Download Mandala",
                    data=byte_im,
                    file_name=f"mandala_{inspiration}.png",
                    mime="image/png",
                )

# Footer
st.markdown("---")
st.markdown("This app uses OpenAI's DALL-E 3 model to generate unique mandala art.")
st.markdown("Note: Each generation uses API credits from your OpenAI account.")