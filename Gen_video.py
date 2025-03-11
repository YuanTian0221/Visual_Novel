import os
import subprocess

# ✅ Number of files (Modify this according to your dataset)
num_files = 4  
video_list = []  # Store generated video filenames

# ✅ Ensure the output directory exists
os.makedirs("videos/The_Call_of_Cthulhu", exist_ok=True)

# ✅ Loop through each scene to generate individual videos
for i in range(1, num_files + 1):
    img_file = f"images/The_Call_of_Cthulhu/generated_image_{i}.png"  # Input image file
    audio_file = f"voices/The_Call_of_Cthulhu/MP3_{i}.mp3"  # Input audio file
    output_video_file = f"videos/The_Call_of_Cthulhu/temp_video_{i}.mp4"  # Output video file

    # ✅ Generate a single video using FFmpeg
    ffmpeg_cmd = [
        "ffmpeg", "-loop", "1", "-i", img_file,  # Load image as a still frame
        "-i", audio_file,  # Load audio file
        "-c:v", "libx264", "-tune", "stillimage",  # Encode video using H.264 codec optimized for still images
        "-c:a", "aac", "-b:a", "192k",  # Encode audio using AAC codec with 192kbps bitrate
        "-pix_fmt", "yuv420p",  # Set pixel format for broad compatibility
        "-shortest", output_video_file  # Ensure video duration matches audio length
    ]

    # ✅ Execute FFmpeg command
    subprocess.run(ffmpeg_cmd, check=True)
    video_list.append(f"temp_video_{i}.mp4")  # Store generated video filename

    print(f"✅ Video generated: {output_video_file}")

# ✅ Create a file list for concatenation
concat_file = "videos/The_Call_of_Cthulhu/video_list.txt"
with open(concat_file, "w") as f:
    for video in video_list:
        f.write(f"file '{video}'\n")

# ✅ Concatenate all videos into a final output file
final_output = "Output/final_output.mp4"
ffmpeg_concat_cmd = [
    "ffmpeg", "-f", "concat", "-safe", "0", "-i", concat_file,  # Use FFmpeg to concatenate videos
    "-c", "copy", final_output  # Copy streams without re-encoding
]

subprocess.run(ffmpeg_concat_cmd, check=True)
print(f"✅ Video concatenation complete: {final_output}")
