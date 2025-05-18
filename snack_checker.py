import os
import json
import streamlit as st
from PIL import Image
from io import BytesIO
from tempfile import NamedTemporaryFile
import easyocr
import random

from phi.agent import Agent
from phi.model.google import Gemini
from phi.tools.tavily import TavilyTools

# Load API keys from config.json
with open("config.json") as config_file:
    config = json.load(config_file)

# Set API keys correctly
os.environ['TAVILY_API_KEY'] = config['TAVILY_API_KEY']
os.environ['GOOGLE_API_KEY'] = config['GOOGLE_API_KEY']

# System Prompt for AI
SYSTEM_PROMPT = """
You are an expert Food Product Analyst specializing in nutrition and health effects of ingredients.
Your job is to analyze product ingredients and assess their impact.
Consider:
- The nutritional impact of the product.
- Artificial additives, preservatives, and harmful chemicals.
- Provide a clear, science-backed summary including risks and better alternatives.
* Also rate the ingredients with a 1-5 star rating.
* Use emojis to make the analysis more engaging and fun.
* Share some interesting, little-known facts about the ingredients that will make people rethink their favorite snack/food/product.
* Score the product/food/snack from 1-5 (1 being the worst and 5 being the best).
"""

# Instructions for the AI agent
INSTRUCTIONS = """
* Analyze the list of ingredients carefully.
* Highlight harmful additives, preservatives, and chemicals.
* Explain the nutritional value and potential risks.
* Suggest healthier alternatives if necessary.
* Rate the ingredients from 1-5 stars.
* Make the explanation fun, engaging, and easy to understand by using emojis and bold important terms.
"""

# Initialize AI agent
def get_agent():
    return Agent(
        model=Gemini(id="gemini-2.0-flash-exp"),
        system_prompt=SYSTEM_PROMPT,
        instructions=INSTRUCTIONS,
        tools=[TavilyTools(api_key=os.getenv("TAVILY_API_KEY"))],
        markdown=True,
    )

# Extract text from image using EasyOCR
def extract_text_from_image(image_path):
    reader = easyocr.Reader(['en'])
    result = reader.readtext(image_path, detail=0)
    return " ".join(result)

# Generate random rating
def generate_rating():
    return random.randint(1, 5)

# Analyze ingredients
def analyze_ingredients(image_path, health_problem=None):
    extracted_text = extract_text_from_image(image_path)  # Extract ingredients
    
    if not health_problem:
        health_problem = "general product analysis"

    agent = get_agent()
    response = agent.run(f"""
        The user has a health problem: {health_problem}
        Analyze the ingredients: {extracted_text}
        Identify any harmful ingredients, nutritional impacts, and provide a 1-5 star rating.
        Suggest healthier alternatives if needed.
        Make sure to include **emojis** and **bold important terms** to make the summary more fun and engaging!
    """)

    # Modify response content
    rating = generate_rating()
    formatted_response = f"\n🌟 **Rating:** {rating} / 5 🌟\n\n"
    response_content = response.content
    response_content = response_content.replace("preservatives", "**preservatives** ⚠️")
    response_content = response_content.replace("chemicals", "**chemicals** 🧪")
    response_content = response_content.replace("additives", "**additives** 🍭")
    response_content = response_content.replace("healthier alternatives", "🍏 **healthier alternatives** 🍎")
    response_content = response_content.replace ("rating", "**unhealthy**" ,)

    # Add some fun emojis throughout the summary
    response_content += f"\n\n🎉 Overall Rating: {rating} ⭐\n\n✨ Stay healthy and enjoy your food! ✨"

    formatted_response += response_content
    return formatted_response

# Save uploaded file temporarily
def save_uploaded_file(uploaded_file):
    with NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
        tmp_file.write(uploaded_file.getbuffer())
        return tmp_file.name

# Streamlit UI
def main():
    st.title("Debugging America! 🍔⚠️🕵")
    st.write("Created by OpenSite.co (Liz)")

    uploaded_file = st.file_uploader("Upload an image of the ingredient list 📥", type=["jpg", "jpeg", "png"])

    health_problem = st.text_input("What health issues do you have? 🩺 💉 Get to the root of your problems (Optional)")

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", width=300)

        temp_path = save_uploaded_file(uploaded_file)

        if st.button("🔍 Analyze Ingredients & Health Impact"):
            import time
            # Display the initial "Please wait thinking" message once
            st.success("✅ Please Wait Thinking ......🧐!")

            # Initialize progress bar
            progress_bar = st.progress(0)

            # Loop to update the progress bar
            for num in range(100):
                progress_bar.progress(num)  # Update progress bar
                time.sleep(0.01)  # Speed up the progress bar update

            # Once the progress is complete, show the "Analysis complete" message
            st.success("✅Almost Ready😴💤....Analysis is being created!😎 ")

            # Release confetti for a few seconds
            time.sleep(0.1)
            st.balloons()

            # Now that the progress is complete, display the analysis result
            analysis_result = analyze_ingredients(temp_path, health_problem)
            st.write(analysis_result)
            
            # Clean up the temporary file
            os.unlink(temp_path)

    elif not uploaded_file and health_problem:
        st.warning("Please upload an image to analyze.")

if __name__ == "__main__":
    main()

