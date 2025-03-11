from langchain.prompts import PromptTemplate
import json
import requests
import time
import os  # Used to create directories
import openai

# ✅ Load the Visual_Style configuration file
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

visual_style = config["Visual_Style"]  # Retrieve the Lovecraftian horror style settings

# ✅ Load the scenes_1.json file
with open("scripts/The_Call_of_Cthulhu/scenes_1.json", "r", encoding="utf-8") as f:
    scene_list = json.load(f)  # Load all scene details

# ✅ Generate image prompts
prompts = []

for scene in scene_list:  
    # Extract scene details
    scene_desc = scene["summary"]
    location = scene["location"]
    characters = ", ".join(scene["characters"])  # Convert character list to a string
    events = ", ".join(scene["events"])  # Convert event list to a string
    
    # ✅ Construct the final prompt using visual style settings
    prompt = (
        f"A {visual_style['mood']} scene set in {visual_style['time_period']}. "
        f"The art style is {visual_style['art_style']}, using {visual_style['color_palette']} colors. "
        f"The environment is {visual_style['details']['environment']} under {visual_style['details']['weather']}. "
        f"The setting is {location}, featuring {characters}. "
        f"Key events happening in this scene: {events}. "
        f"The scene is illuminated by {visual_style['details']['lighting']}. "
        f"Scene description: {scene_desc}."
    )
    
    prompts.append(prompt)

# ✅ Output all generated prompts
for i, p in enumerate(prompts):
    print(f"Prompt {i + 1}: {p}\n")
    
# **📂 Directory to save generated images**
save_dir = "images/The_Call_of_Cthulhu"

# **📌 Check and create directory if it does not exist**
os.makedirs(save_dir, exist_ok=True)

# **🎨 Loop through prompts to generate images**
for i, prompt in enumerate(prompts):
    try:
        print(f"Generating image {i + 1} / {len(prompts)}: {prompt}")

        # **🖼️ Generate the image using DALL·E 3**
        response = openai.Image.create(
            prompt=prompt,
            model="dall-e-3",  # Uses the DALL·E 3 model
            n=1,  # Generates 1 image per request
            size="1024x1024"  # Image resolution
        )

        # **🔗 Retrieve the image URL from the response**
        image_url = response["data"][0]["url"]
        print(f"✅ Image {i + 1} generated successfully, URL: {image_url}")

        # **📥 Download the image**
        img_data = requests.get(image_url).content
        file_name = os.path.join(save_dir, f"generated_image_{i + 1}.png")
        with open(file_name, "wb") as img_file:
            img_file.write(img_data)

        print(f"📂 Image saved as {file_name}\n")

        # **⏳ Delay to avoid API rate limits**
        time.sleep(2)

    except Exception as e:
        print(f"❌ Error generating image {i + 1}: {e}\n")
