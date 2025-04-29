import feedparser
import google.generativeai as genai
from gtts import gTTS
from moviepy.editor import *
import os
import requests
from PIL import Image, ImageDraw, ImageFont
import io
import numpy as np
import sys
import re
import textwrap

# Configure ImageMagick paths
os.environ["IMAGEMAGICK_BINARY"] = r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"
os.environ["CONVERT_BINARY"] = r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\convert.exe"

# Step 1: Gemini Setup
GEMINI_API_KEY = "AIzaSyCfwWLbjQlwz90FsU98mPcNoKHTi4sn7g0"
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Step 2: Get trending news
def get_trending_news():
    feed = feedparser.parse("https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en")
    article = feed.entries[0]
    return article.title, article.summary

# Step 3: Generate script
def generate_script(title, summary):
    prompt = f"""Create a detailed and engaging video script for this news article. The script should be informative, well-structured, and easy to follow.

    Requirements:
    1. Create 10-15 concise lines that tell a complete story
    2. Start with a strong hook to grab attention
    3. Include key facts, figures, and important details
    4. Explain the context and background where relevant
    5. Highlight the main points and their significance
    6. End with a clear conclusion or forward-looking statement
    7. Keep each line under 50 characters for optimal display
    8. Use clear, conversational language
    9. Avoid technical jargon unless necessary
    10. Format as complete sentences without any markers or labels

    Article Details:
    Title: {title}
    Summary: {summary}

    Please generate a script that covers all important aspects of the story while maintaining viewer engagement."""
    
    response = model.generate_content(prompt)
    # Clean up the response text
    script = response.text
    # Remove any remaining asterisks or formatting
    script = re.sub(r'\*\*|\*|Voiceover:', '', script)
    # Split into lines and clean each line
    lines = [line.strip() for line in script.split('\n') if line.strip()]
    return '\n'.join(lines)

# Step 4: Generate image prompt
def generate_image_prompt(script):
    prompt = f"""Create a detailed prompt for generating a background image for this video script.
    The image should be relevant to the content and suitable for text overlay.
    
    Script: {script}
    
    Return only the image prompt, nothing else."""
    
    response = model.generate_content(prompt)
    return response.text

# Step 5: Generate video
def create_video(script, image_prompt):
    try:
        # Create necessary directories
        os.makedirs("audio", exist_ok=True)
        os.makedirs("videos", exist_ok=True)
        
        # Generate TTS audio
        tts = gTTS(text=script, lang='en')
        tts_path = "audio/narration.mp3"
        tts.save(tts_path)
        
        # Get audio duration
        audio = AudioFileClip(tts_path)
        duration = audio.duration
        
        # Create a solid color background (dark blue)
        width, height = 1920, 1080  # Full HD resolution
        color = np.array([[[0, 0, 100]]], dtype=np.uint8)  # Dark blue
        background = np.tile(color, (height, width, 1))
        
        # Create video
        clip = ImageClip(background, duration=duration)
        
        # Split script into lines for better text rendering
        script_lines = script.split('\n')
        text_clips = []
        
        # Calculate total height needed for all text
        total_lines = len(script_lines)
        line_height = 60  # Increased line height for better readability
        total_text_height = total_lines * line_height
        start_y = (height - total_text_height) // 2  # Center vertically
        
        for i, line in enumerate(script_lines):
            if line.strip():  # Skip empty lines
                # Create text image using PIL
                text_img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
                draw = ImageDraw.Draw(text_img)
                font = ImageFont.truetype("arial.ttf", 40)  # Increased font size
                
                # Wrap text if it's too long
                wrapped_lines = textwrap.wrap(line.strip(), width=40)
                 
                # Draw each wrapped line
                for j, wrapped_line in enumerate(wrapped_lines):
                    # Get text size using getbbox
                    bbox = draw.textbbox((0, 0), wrapped_line, font=font)
                    text_width = bbox[2] - bbox[0]
                    
                    # Center each line horizontally
                    x = (width - text_width) // 2
                    y = start_y + (i * line_height) + (j * line_height)
                    
                    # Draw text with outline for better visibility
                    # Draw outline
                    outline_color = (0, 0, 0, 255)
                    for offset_x, offset_y in [(-1,-1), (-1,1), (1,-1), (1,1)]:
                        draw.text((x+offset_x, y+offset_y), wrapped_line, font=font, fill=outline_color)
                    # Draw main text
                    draw.text((x, y), wrapped_line, font=font, fill=(255, 255, 255, 255))
                
                # Convert PIL image to numpy array
                text_array = np.array(text_img)
                text_clip = ImageClip(text_array, duration=duration)
                text_clips.append(text_clip)
        
        # Combine all clips
        video = CompositeVideoClip([clip] + text_clips).set_audio(audio)
        video_path = "videos/output_video.mp4"
        video.write_videofile(video_path, fps=24, codec='libx264', audio_codec='aac')
        
        return video_path
        
    except Exception as e:
        print(f"Error creating video: {str(e)}")
        print("\nMake sure you have the required fonts installed.")
        print("You can download Arial font from: https://www.fonts.com/font/monotype/arial")
        sys.exit(1)

def main():
    print("Starting video generation process...")
    
    # Get trending news
    print("Fetching trending news...")
    title, summary = get_trending_news()
    print(f"News: {title}\n{summary}")
    
    # Generate script
    print("\nGenerating script...")
    script = generate_script(title, summary)
    print(f"Generated Script:\n{script}")
    
    # Generate image prompt
    print("\nGenerating image prompt...")
    image_prompt = generate_image_prompt(script)
    print(f"Image Prompt: {image_prompt}")
    
    # Create video
    print("\nCreating video...")
    video_path = create_video(script, image_prompt)
    print(f"\nVideo created successfully! Saved to: {video_path}")

if __name__ == "__main__":
    main()
