from bs4 import BeautifulSoup
import os
import re
import requests

piece_regex = re.compile( "\w+ \((\w)\)" )

url = "https://commons.wikimedia.org/wiki/Category:SVG_chess_pieces"
page = requests.get(url)

base_dir = "skins/skin2"

soup = BeautifulSoup(page.content, "html.parser")
target = soup.select(".wikitable")[1]

for row in target.select('tr')[2:2+7]:
    # get piece label
    header_element = row.select_one('th')
    header = header_element.text
    mo = piece_regex.search(header)

    if mo: 
        notation = mo.group(1)
        images = row.select("td a img")[:2]
        
        for index, image in enumerate(images):
            print(f"Downloading {image.get('src')}")
            color = "b" if index == 0 else "w"

            img_response = requests.get( image.get('src') )
            colored_piece_dir = os.path.join(base_dir, color)

            if not os.path.exists(colored_piece_dir):
                os.makedirs(colored_piece_dir)
            
            if img_response.status_code == 200:
                path_to_file = os.path.join( colored_piece_dir, f"{notation}.png")

                with open( path_to_file, "wb" ) as __:
                    __.write(img_response.content)
                    print(f"Successfully saved {image.get('src')} to {path_to_file}")
            
            else:
                print(f"Error downloading {image.get('src')}. Status code: {img_response.status_code}")
