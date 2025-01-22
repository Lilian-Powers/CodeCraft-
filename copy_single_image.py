
import os
import shutil

def copy_image(index, source_name):
    if not os.path.exists('static'):
        os.makedirs('static')
        print("Created static directory")
    
    source_path = os.path.join('attached_assets', source_name)
    dest_name = f'project_showcase{index}.jpg'
    dest_path = os.path.join('static', dest_name)
    
    try:
        shutil.copy2(source_path, dest_path)
        print(f'Successfully copied {source_name} to {dest_name}')
    except Exception as e:
        print(f'Error copying file: {str(e)}')

# Copy each image
images = [
    'Screenshot_20250102-104625~2[1].jpg',  # Chat Bot
    'Screenshot_20250102-104851~2[1].jpg',  # Story Creator
    'Screenshot_20250102-104949~2[1].jpg',  # Temperature Converter
    'Screenshot_20250120-185216~2[1].jpg',  # Compliment Generator
    'Screenshot_20250120-185232~2[1].jpg',  # Vacation Planner
    'Screenshot_20250120-185248~2[1].jpg'   # Food Adventure
]

for i, img in enumerate(images, 1):
    copy_image(i, img)
