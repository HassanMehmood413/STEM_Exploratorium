import os
import time
from dotenv import load_dotenv
from PIL import Image
import streamlit as st
from openai import OpenAI
import anthropic

# Load environment variables
load_dotenv()

# Initialize OpenAI client using AIML API
client = OpenAI(
    api_key=st.secrets["API_KEY"],  # Update with your environment variable for the API key
    base_url="https://api.aimlapi.com",
)

# Initialize Anthropic client
anthropic_client = anthropic.Anthropic(
    api_key=st.secrets["ANTHROPIC"]  # Your Anthropic API key
)

def generate_response(prompt):
    response = client.chat.completions.create(
        model="o1-mini",  
        messages=[{"role": "user", "content": prompt}],
        max_tokens=512,  
    )
    return response.choices[0].message.content if response.choices else "No response generated."

def fallback_to_anthropic(prompt):
    message = anthropic_client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=512,  
        temperature=0,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content

def stream_data(data):
    for word in data.split(" "):
        yield word + " "
        time.sleep(0.05)

def main():
    st.set_page_config(page_title="TEM Exploratorium", layout="wide")

    # Add header image and title
    col1, col2 = st.columns([1, 10])  # Adjust column sizes to make the text closer
    with col1:
        st.image("images/stem.png", width=100)  # Adjusted width for a smaller image
    with col2:
        st.markdown("<h1 style='text-align: left;'>TEM Exploratorium</h1>", unsafe_allow_html=True)

    st.markdown("### Welcome to STEM Exploratorium!")
    st.markdown("Explore STEM concepts through hands-on activities, virtual field trips, and collaborative projects!")

    # Purpose paragraph
    st.markdown(
        """
        The STEM Exploratorium is designed to inspire curiosity and creativity in science, technology, engineering, and mathematics. 
        Whether you're looking for engaging DIY projects, exciting virtual field trips, or challenging STEM activities, 
        this app provides a platform to explore, learn, and innovate. Join us on this journey to discover the wonders of STEM!
        """
    )

    # Sidebar for controls
    with st.sidebar:
        st.header("Explore STEM Topics")
        activity_type = st.selectbox("Select Activity Type", ["DIY Project", "Virtual Field Trip", "Challenge"])
        topic = st.text_input("Enter a STEM topic or project name:")
        project_count = st.number_input("How many project ideas would you like to generate?", min_value=1, max_value=10, value=3)
        image_upload = st.file_uploader("Upload an image related to your STEM project:")

        generate_btn = st.button("Generate")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Generated Ideas/Content:")
        if generate_btn and topic:
            if activity_type == "DIY Project":
                prompt = f"Generate {project_count} DIY project ideas for the STEM topic: {topic}."
            elif activity_type == "Virtual Field Trip":
                prompt = f"Suggest virtual field trip ideas related to the STEM topic: {topic}."
            elif activity_type == "Challenge":
                prompt = f"Create a STEM challenge for the topic: {topic}."

            output = generate_response(prompt)

            if len(output.split()) < 50:
                st.write("The initial response was too short. Generating a more detailed response...")
                output = fallback_to_anthropic(prompt)

            st.write_stream(stream_data(output))
        else:
            st.write("Please enter a topic and select an activity type.")

    with col2:
        st.subheader("Upload an Image for Analysis:")
        if image_upload is not None:
            img = Image.open(image_upload)
            st.image(img, caption='Uploaded Image.', use_column_width=True)
            st.write("Image uploaded! Further analysis can be integrated.")

    # Add disclaimer at the bottom of the page
    st.markdown("---")
    st.markdown("*Response can be according to the Free API*")

if __name__ == "__main__":
    main()