from pathlib import Path
import openai
import json
from gtts import gTTS  # Google Text-to-Speech (optional alternative)

# ✅ Load the scenes_1.json file
with open("scripts/The_Call_of_Cthulhu/scenes_1.json", "r", encoding="utf-8") as f:
    scene_list = json.load(f)  # Read all scene data

inputs = []  # Store scene text inputs for speech synthesis

# ✅ Iterate through each scene to generate speech
for i, scene in enumerate(scene_list):
    # Extract the original scene text
    input_text = scene["original_text"]

    # ✅ Generate speech using OpenAI TTS
    response = openai.Audio.speech.create(
        model="tts-1",  # Select the text-to-speech model (options: tts-1, tts-1-hd)
        voice="onyx",  # Choose a voice (options: alloy, echo, fable, onyx, nova, shimmer)
        input=input_text  # The text content to be converted into speech
    )

    # ✅ Save the generated audio file
    output_path = f"voice/The_Call_of_Cthulhu/MP3_{i + 1}.mp3"
    response.stream_to_file(output_path)  # Stream the response directly to a file

    print(f"🎵 Audio saved as {output_path}")

# ✅ List available voices in OpenAI TTS
openai.audio.speech.list()
