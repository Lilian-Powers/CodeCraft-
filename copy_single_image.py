
import os
import shutil

# Create static directory if it doesn't exist
if not os.path.exists('static'):
    os.makedirs('static')
    print("Created static directory")

# Define all the images we want to copy
image_mapping = {
    'Screenshot_20250102-104625~2[1].jpg': 'project_showcase1.jpg',  # Chat Bot
    'Screenshot_20250102-104851~2[1].jpg': 'project_showcase2.jpg',  # Story Creator
    'Screenshot_20250102-104949~2[1].jpg': 'project_showcase3.jpg',  # Temperature Converter
    'Screenshot_20250120-185216~2[1].jpg': 'project_showcase4.jpg',  # Compliment Generator
    'Screenshot_20250120-185232~2[1].jpg': 'project_showcase5.jpg',  # Vacation Planner
    'Screenshot_20250120-185248~2[1].jpg': 'project_showcase6.jpg',  # Food Adventure
    'Screenshot_20250120-185310~2[1].jpg': 'project_showcase7.jpg',  # Additional Project
    'Screenshot_20250120-185320~2[1].jpg': 'project_showcase8.jpg',  # Additional Project
    'Screenshot_20250120-185329~2[1].jpg': 'project_showcase9.jpg',  # Additional Project
}

for source, dest in image_mapping.items():
    source_path = os.path.join('attached_assets', source)
    dest_path = os.path.join('static', dest)
    
    try:
        if os.path.exists(source_path):
            shutil.copy2(source_path, dest_path)
            print(f'Successfully copied {source} to {dest}')
        else:
            print(f'Source file not found: {source}')
    except Exception as e:
        print(f'Error copying {source}: {str(e)}')

print("Image copying process completed")
