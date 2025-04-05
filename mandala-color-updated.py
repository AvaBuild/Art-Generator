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
    
    # Get color name from hex code - this is the main improvement
    color_rgb = tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    
    # Basic color naming based on RGB values
    def get_color_name(rgb):
        r, g, b = rgb
        # Define some common color names
        if r > 200 and g < 100 and b < 100:
            return "red"
        elif r > 200 and g > 150 and b < 100:
            return "orange"
        elif r > 200 and g > 200 and b < 100:
            return "yellow"
        elif r < 100 and g > 200 and b < 100:
            return "green"
        elif r < 100 and g < 100 and b > 200:
            return "blue"
        elif r > 150 and g < 100 and b > 150:
            return "purple"
        elif r > 200 and g > 150 and b > 200:
            return "pink"
        elif r < 100 and g > 150 and b > 150:
            return "teal"
        elif r > 200 and g > 200 and b > 200:
            return "white"
        elif r < 100 and g < 100 and b < 100:
            return "black"
        elif r > g and r > b:
            return f"reddish ({color.upper()})"
        elif g > r and g > b:
            return f"greenish ({color.upper()})"
        elif b > r and b > g:
            return f"bluish ({color.upper()})"
        else:
            return f"custom color ({color.upper()})"
    
    color_name = get_color_name(color_rgb)
    st.write(f"Selected color: {color_name}")
    
    # API Key input with password masking
    api_key = st.text_input("Enter your OpenAI API Key:", type="password", help="Your API key will not be stored")
    
    # Submit button
    submitted = st.form_submit_button("Generate Mandala")

# Function to generate image
def generate_mandala(inspiration, color, color_name):
    # Create the prompt for DALL-E - UPDATED FOR BETTER COLOR SPECIFICATION
    prompt = f"""Create a beautiful, symmetrical mandala inspired by '{inspiration}'.
The mandala MUST prominently feature the color {color_name} ({color}) as a main color throughout the design.
Use {color_name}, black, and white as the primary colors, with {color_name} being the dominant accent.
The mandala should be intricate, detailed, and suitable for printing.
Make it perfectly centered and balanced with clear patterns.
The final image must be a mandala with {color_name} clearly visible as a key element in the design."""
    
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
            image, image_url = generate_mandala(inspiration, color, color_name)
            
            if image:
                # Display the generated image
                st.success("✅ Your mandala has been generated!")
                st.image(image, caption=f"Mandala inspired by '{inspiration}' with {color_name}", use_column_width=True)
                
                # Convert PIL image to bytes for download
                buf = io.BytesIO()
                image.save(buf, format="PNG")
                byte_im = buf.getvalue()
                
                # Download button
                st.download_button(
                    label="Download Mandala",
                    data=byte_im,
                    file_name=f"mandala_{inspiration}_{color_name.replace(' ', '_')}.png",
                    mime="image/png",
                )

# Footer
st.markdown("---")
st.markdown("This app uses OpenAI's DALL-E 3 model to generate unique mandala art.")
st.markdown("Note: Each generation uses API credits from your OpenAI account.")