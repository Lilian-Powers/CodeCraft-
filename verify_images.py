
import os
import shutil

def verify_and_copy_images():
    print("Starting verification process...")
    
    # Check source directory
    if not os.path.exists('attached_assets'):
        print("ERROR: attached_assets directory does not exist!")
        return
        
    # Create static directory if needed
    if not os.path.exists('static'):
        os.makedirs('static')
        print("Created static directory")
    
    # List all files in attached_assets
    source_files = os.listdir('attached_assets')
    print("\nFiles in attached_assets:")
    for file in source_files:
        print(f"- {file}")
    
    # Try to copy each image
    for i in range(1, 12):
        source_name = f'Screenshot_20250102-104625~2[1].jpg'  # Example filename
        dest_name = f'project_showcase{i}.jpg'
        
        source_path = os.path.join('attached_assets', source_name)
        dest_path = os.path.join('static', dest_name)
        
        print(f"\nAttempting to copy {source_name} to {dest_name}")
        if os.path.exists(source_path):
            try:
                shutil.copy2(source_path, dest_path)
                print(f"Successfully copied to {dest_path}")
            except Exception as e:
                print(f"Error copying file: {str(e)}")
        else:
            print(f"Source file not found: {source_path}")
    
    # Verify results
    print("\nFiles in static directory after copy:")
    if os.path.exists('static'):
        print(os.listdir('static'))
    else:
        print("Static directory not found!")

if __name__ == '__main__':
    verify_and_copy_images()
