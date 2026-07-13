from PIL import Image, ImageDraw, ImageFont
import urllib.request
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
LOGO_PATH = BASE_DIR / "dashboard" / "assets" / "logo.png"
OUTPUT_PATH = BASE_DIR / "dashboard" / "assets" / "logo_with_text.png"

def create_logo_with_text():
    if not LOGO_PATH.exists():
        print("Logo não encontrada!")
        return

    # Open original logo
    logo = Image.open(LOGO_PATH).convert("RGBA")
    
    # Resize logo to standard height (e.g., 60px)
    target_height = 60
    aspect_ratio = logo.width / logo.height
    new_width = int(target_height * aspect_ratio)
    logo = logo.resize((new_width, target_height), Image.Resampling.LANCZOS)
    
    # Text parameters
    text = "CommercePulse"
    
    # Try to load a nice font, fallback to default
    try:
        font = ImageFont.truetype("arialbd.ttf", 36)
    except IOError:
        font = ImageFont.load_default()
        
    # Create a temporary image just to measure text size
    temp_img = Image.new('RGB', (1, 1))
    draw = ImageDraw.Draw(temp_img)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Create final image with space for logo + text + padding
    padding = 15
    total_width = new_width + padding + text_width + 10
    total_height = max(target_height, text_height) + 10
    
    # Create transparent background
    final_img = Image.new("RGBA", (total_width, total_height), (255, 255, 255, 0))
    
    # Paste logo
    y_logo = (total_height - target_height) // 2
    final_img.paste(logo, (0, y_logo), logo)
    
    # Draw text
    draw = ImageDraw.Draw(final_img)
    y_text = (total_height - text_height) // 2 - 5 # slight visual adjustment
    draw.text((new_width + padding, y_text), text, fill=(248, 250, 252), font=font)
    
    final_img.save(OUTPUT_PATH)
    print("Logo with text created successfully!")

if __name__ == "__main__":
    create_logo_with_text()
