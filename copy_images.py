
import shutil
import os

def copy_and_rename_images():
    # Create static directory if it doesn't exist
    if not os.path.exists('static'):
        os.makedirs('static')

    # Mapping of source files to their new names
    file_mapping = {
        'Screenshot_20250102-104625~2[1].jpg': 'project_showcase1.jpg',
        'Screenshot_20250102-104851~2[1].jpg': 'project_showcase2.jpg',
        'Screenshot_20250102-104949~2[1].jpg': 'project_showcase3.jpg',
        'Screenshot_20250120-185216~2[1].jpg': 'project_showcase4.jpg',
        'Screenshot_20250120-185232~2[1].jpg': 'project_showcase5.jpg',
        'Screenshot_20250120-185248~2[1].jpg': 'project_showcase6.jpg',
        'Screenshot_20250120-185310~2[1].jpg': 'project_showcase7.jpg',
        'Screenshot_20250120-185320~2[1].jpg': 'project_showcase8.jpg',
        'Screenshot_20250120-185329~2[1].jpg': 'project_showcase9.jpg',
        'Screenshot_20250120-185342~2[1].jpg': 'project_showcase10.jpg',
        'Screenshot_20250120-185402~2[1].jpg': 'project_showcase11.jpg'
    }

    # Copy and rename files
    for source, dest in file_mapping.items():
        source_path = os.path.join('attached_assets', source)
        dest_path = os.path.join('static', dest)
        if os.path.exists(source_path):
            shutil.copy2(source_path, dest_path)
            print(f'Copied {source} to {dest}')

if __name__ == '__main__':
    copy_and_rename_images()
