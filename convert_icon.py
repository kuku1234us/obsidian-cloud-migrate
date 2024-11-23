from PIL import Image
import os

def convert_to_ico():
    input_path = os.path.join('assets', 'appicon.png')
    output_path = os.path.join('assets', 'appicon.ico')
    
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} not found")
        return
        
    # Open the PNG image
    img = Image.open(input_path)
    
    # Convert to RGBA if not already
    img = img.convert('RGBA')
    
    # Create ICO file
    img.save(output_path, format='ICO')
    print(f"Successfully converted {input_path} to {output_path}")

if __name__ == '__main__':
    convert_to_ico()
