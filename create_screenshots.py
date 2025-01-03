
from PIL import Image, ImageDraw, ImageFont
import os

def create_screenshot(filename, text, size=(800, 600), bg_color=(25, 35, 45), text_color=(255, 255, 255)):
    img = Image.new('RGB', size, bg_color)
    draw = ImageDraw.Draw(img)
    
    # Draw text in center
    text_position = (size[0]//2, size[1]//2)
    draw.text(text_position, text, fill=text_color, anchor="mm", font=None)
    
    # Save the image
    img.save(f'static/screenshots/{filename}.png')

# Create screenshots
create_screenshot('homepage', 'CodeCraft Homepage')
create_screenshot('editor', 'Code Editor Interface')
create_screenshot('tutorials', 'Tutorials Page')
