
import shutil
import os

def copy_and_rename_images():
    print("Starting image copy process...")
    
    # Create static directory if it doesn't exist
    if not os.path.exists('static'):
        os.makedirs('static')
        print("Created static directory")

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

    total_files = len(file_mapping)
    copied_files = 0

    # Copy and rename files
    for source, dest in file_mapping.items():
        source_path = os.path.join('attached_assets', source)
        dest_path = os.path.join('static', dest)
        try:
            if os.path.exists(source_path):
                shutil.copy2(source_path, dest_path)
                copied_files += 1
                print(f'Successfully copied {source} to {dest} ({copied_files}/{total_files})')
            else:
                print(f'Warning: Source file not found - {source}')
        except Exception as e:
            print(f'Error copying {source}: {str(e)}')

    print(f"\nProcess completed: {copied_files} files copied out of {total_files}")

if __name__ == '__main__':
    copy_and_rename_images()
