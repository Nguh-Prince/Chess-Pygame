import os
import re

from PIL import Image

default_skin_directory = os.path.join(
    os.path.dirname(__file__), "skins", "default"
)

extension_regex = re.compile(r"(.*)\.(.*)$")

supported_extensions = ["png", "jpg", "jpeg"]

def resize_piece_images_in_skin_directory(skin_directory: str=default_skin_directory, image_size: tuple=None):
    """
    Resize all the images in the skin_directory to image_size
    """
    if not os.path.exists(skin_directory):
        raise FileNotFoundError(f"The {skin_directory} directory does not exist")

    if not os.path.isdir(skin_directory):
        raise ValueError(f"The path {skin_directory} is not a directory")

    if image_size is None:
        image_size = (15, 15)

    colors = ["b", "w"]

    for color in colors:
        color_directory = os.path.join( skin_directory, color )

        for file in os.listdir(color_directory):
            file_path = os.path.join(color_directory, file)

            if os.path.isfile(file_path):
                extension = extension_regex.search(file)
                
                if extension.group(2) in supported_extensions:
                    captured_image_file_directory = os.path.join(color_directory, "captured")
                    
                    if not os.path.exists(captured_image_file_directory):
                        os.makedirs(captured_image_file_directory)

                    captured_image_file_path = os.path.join(captured_image_file_directory, file)

                    # open with pillow and resize
                    image = Image.open(file_path)
                    image = image.resize( image_size )

                    image.save(captured_image_file_path)
                else:
                    print(f"The extension {extension.group(1)} of the file {file_path} is not in the list of supported extensions")

resize_piece_images_in_skin_directory()
