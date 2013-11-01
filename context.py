#!/usr/bin/env python3

"""Context Free Meme

Usage:
    cf_meme.py CAPTION
    cf_meme.py -f CAPTION_FILE
    cf_meme.py (-h | --help)
    cf_meme.py --version

Options:
    -h --help   Show this help
    --version   Show version
"""

import hashlib
import io
import os
import sys

from docopt import docopt
import requests
from PIL import Image, ImageDraw, ImageFont

class Caption(object):
    """A caption and methods on that to turn it into a meme."""

    def __init__(self, caption, uid=None):
        """Creates a new Caption with the given caption."""
        self.caption = caption
        self._uid = uid

    @property
    def uid(self):
        """Returns the uid for caption."""
        if self._uid is None:
            md5 = hashlib.md5(bytes(self.caption, 'utf-8'))
            self._uid = md5.hexdigest()[:8]
        return self._uid

    def exists(self):
        """Returns whether a meme exists for this caption."""
        extentions = ['jpeg', 'jpg', 'png', 'gif']
        for extention in extentions:
            if os.path.isfile('{}.{}'.format(self.uid, extention)):
                return True
        return False

    def __repr__(self):
        return '<Caption("{0.caption}", uid={0.uid})>'.format(self)


def get_image_urls(caption):
    """Finds and returns urls to possible images for the caption."""
    url = 'http://ajax.googleapis.com/ajax/services/search/images'
    payload = {
        'v': '1.0',
        'rsz': '5',
        'imgsz': 'xxlarge',
        'safe': 'active',
        'q': caption.caption,
    }

    try:
        response = requests.get(url, params=payload)
        if response.status_code == 200:
            json = response.json()
            results = json['responseData']['results']
            return [result['url'] for result in results]
    except IOError as err:
        print("Error searching for images for {}".format(caption), err)

    return []

def download_image(caption):
    """Downloads and returns the image"""
    urls = get_image_urls(caption)
    for url in urls:
        try:
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                return Image.open(io.BytesIO(response.content))
        except IOError as err:
            print("Error downloading image for {}".format(caption), err)
    return None

def memer(caption):
    """Turns a caption into a meme."""
    if caption.exists():
        return True

    image = download_image(caption)
    if image is None:
        print("Didnt' find an image for {}".format(caption.caption))
        return

    width, height = image.size
    draw = ImageDraw.Draw(image)

    # Determine font size
    text_width = 1000000
    fontsize = 200
    while text_width + 10 > width:
        fontsize -= 10
        font = ImageFont.truetype('Aller_Std_Rg.ttf', fontsize)
        text_width, text_height = draw.textsize(caption.caption, font)

    # Determine text size
    text_x = (width - text_width) / 2
    text_y = ((height - text_height) / 6) * 5

    # Draw border
    stroke = "black"
    draw.text((text_x-2, text_y-2), caption.caption, font=font, fill=stroke)
    draw.text((text_x+2, text_y-2), caption.caption, font=font, fill=stroke)
    draw.text((text_x-2, text_y+2), caption.caption, font=font, fill=stroke)
    draw.text((text_x+2, text_y+2), caption.caption, font=font, fill=stroke)

    # Draw text
    fill = "white"
    draw.text((text_x, text_y), caption.caption, font=font, fill=fill)

    del draw

    filename = '{}.{}'.format(caption.uid, image.format).lower()
    image.save(filename, image.format)

def get_captions(filename):
    """Returns the captions from the given file."""
    try:
        with open(filename, 'r') as file_handler:
            captions = [line.strip() for line in file_handler]
        return captions
    except IOError as err:
        print('Error opening {}: {}'.format(filename, err))
        sys.exit(1)

def main():
    """Main"""
    args = docopt(__doc__, version='Context Free Meme 0.1')

    if args['CAPTION_FILE'] is not None:
        captions = get_captions(args['CAPTION_FILE'])
    elif args['CAPTION'] is not None:
        captions = [args['CAPTION']]

    for caption in captions:
        memer(Caption(caption))


if __name__ == '__main__':
    main()
