# AI Video Generation Tool

This tool automatically generates short videos from trending news articles using Google's Gemini AI.

## Features

- Fetches trending news from Google News RSS feed
- Generates engaging scripts using Gemini AI
- Creates text-to-speech narration
- Generates videos with text overlays
- Automatically organizes output files

## Prerequisites

- Python 3.8 or higher
- Gemini API key (get it from [Google AI Studio](https://makersuite.google.com/app/apikey))

## Installation

1. Clone this repository
2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Replace `YOUR_GEMINI_API_KEY` in `main.py` with your actual Gemini API key
2. Run the script:
```bash
python main.py
```

The tool will:
1. Fetch the latest trending news
2. Generate a script using Gemini AI
3. Create a video with text overlays and narration
4. Save the output video in the `videos` directory

## Output Structure

The tool creates the following directory structure:
- `audio/`: Contains the generated narration
- `images/`: Contains background images
- `videos/`: Contains the final output videos

## Notes

- The video duration is set to 30 seconds by default
- The script generates 4-5 lines of content suitable for a short video
- Text is displayed in white with a 24pt font size
- Videos are saved in MP4 format at 24fps

## Troubleshooting

If you encounter any issues:
1. Ensure you have a valid Gemini API key
2. Check your internet connection
3. Verify all dependencies are installed correctly
4. Make sure you have write permissions in the current directory 