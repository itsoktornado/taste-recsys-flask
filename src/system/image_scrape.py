import pandas as pd
from bing_image_urls import bing_image_urls

recipe_contents = pd.read_csv('src/data/recipe_contents.csv')

# Can't use images from these URLs (CloudFlare), screw you
# Yes this is a BAD way to do it, but what can you do genius?
ignored_list = [
    'therecipecritic.com',
    'imagesvc',
    'thefoodcharlatan.com',
    'houseofnasheats.com',
    'feelgoodfoodie.net',
    'twopeasandtheirpod.com',
    'indianveggiedelight.com',
]

def getImageUrl(index):
    url = []
    i = 1
    
    while(True):
        if url == [] or any(link in url[-1] for link in ignored_list):
            url = bing_image_urls(recipe_contents['recipe_name'].values[index], limit = i)
            i += 1
        else:
            return url[-1]

# For testing
def getImageUrlText(name):
    url = []
    i = 1
    
    while(True):
        if url == [] or any(link in url[-1] for link in ignored_list):
            url = bing_image_urls(name, limit = i)
            i += 1
        else:
            print(url)
            return url[-1]

print(getImageUrlText("Mango-Peach Smoothie"))
