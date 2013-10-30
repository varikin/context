#!/usr/bin/env python3

import hashlib
import os
import io
import requests
from PIL import Image, ImageDraw, ImageFont

def download_image(url):
    r = requests.get(url, stream=True)
    if r.status_code == 200:
        return r.content
    return None

def meme(image, quote):
    im = Image.open(io.BytesIO(image)) 
    iw, ih = im.size
    draw = ImageDraw.Draw(im)

    # Determine font size 
    tw = 1000000
    fontsize = 200
    while tw + 10 > iw:
        fontsize -= 10
        font = ImageFont.truetype('Aller_Std_Rg.ttf', fontsize)
        tw, th = draw.textsize(quote, font)
   
    # Determine text size 
    sw = (iw - tw) / 2
    sh = ((ih - th) / 6) * 5
    
    # Draw border
    stroke = "black"
    draw.text((sw-3, sh-3), quote, font=font, fill=stroke)
    draw.text((sw+3, sh-3), quote, font=font, fill=stroke)
    draw.text((sw-3, sh+3), quote, font=font, fill=stroke)
    draw.text((sw+3, sh+3), quote, font=font, fill=stroke)
    
    # Draw text
    fill = "white"
    print(quote)
    draw.text((sw, sh), quote, font=font, fill=fill)

    del draw
     
    if iw < 1440 and ih < 900:
        background = Image.new('RGB', (1440, 900), (68, 68, 68))
        background.format = 'JPEG'
        bw = (1440 - iw) // 2
        bh = (900 - ih) // 2
        background.paste(im, (bw, bh))
        im = background
   
    hex = hashlib.md5(bytes(quote, 'utf-8')).hexdigest()[:8]
    filename = '{}.{}'.format(hex, im.format).lower()
    im.save(filename, im.format)


filename = 'quotes.txt'
with open(filename, 'r') as f:
    quotes = [line.strip() for line in f]

google_images = 'http://ajax.googleapis.com/ajax/services/search/images'
basic_payload = {
        'v': '1.0',
        'rsz': '1',
        'imgsz': 'xxlarge',
        'safe': 'active',
}

for quote in quotes:
    payload = dict(basic_payload)
    payload['q'] = quote
    r = requests.get(google_images.format(quote), params=payload)
    if r.status_code == 200:
        json = r.json()
        url = json['responseData']['results'][0]['url']

        image = download_image(url)
        if image:
            meme(image, quote)
    else:
        print("failure: {}".format(quote))


# Google images for each quote
# Add quote to first image

