from gtts import gTTS
import json

# ✅ Load the scenes_1.json file
with open("scripts/The_Call_of_Cthulhu/scenes_1.json", "r", encoding="utf-8") as f:
    scene_list = json.load(f)  # Read all scene data

inputs = []  # Store scene text inputs for speech synthesis

# ✅ Iterate through each scene to generate speech
for i, scene in enumerate(scene_list):
    input_text = scene["original_text"]  # Extract the original scene text

    # ✅ Generate speech using Google Text-to-Speech (gTTS)
    tts = gTTS(text=input_text, lang="en")

    # ✅ Save the generated audio file
    output_path = f"voices/The_Call_of_Cthulhu/MP3_{i + 1}.mp3"
    tts.save(output_path)

    print(f"✅ Audio file generated: {output_path}")