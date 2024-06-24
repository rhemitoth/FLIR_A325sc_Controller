#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
from waveshare_epd import epd2in7_V2
import time
from PIL import Image,ImageDraw,ImageFont
import traceback

def main():
    try:
        # Initialize the display
        epd = epd2in7_V2.EPD()
        epd.init()
        epd.Clear()
        
        #Create a blank image for drawing
        canvas = Image.new('1',(epd.width,epd.height),255)
        draw = ImageDraw.Draw(canvas)
        
        # Load the bitmap image
        image_path = "/home/moorcroftlab/Documents/FLIR/raspi_text_background.bmp"
        bmp_image = Image.open(image_path)
        bw_image = bmp_image.convert('1')
        bmp_width,bmp_height = bw_image.size
        
        # Position to paste the bitmap image
        x_offset = 0
        y_offset = 0
        
        # Paste the bitmap image onto the canvas
        canvas.paste(bw_image,(x_offset,y_offset))
        
        # Load a font
        font_path = "/usr/share/fonts/X11/Type1/NimbusMonoPS-Bold.pfb"
        txt_font = ImageFont.truetype(font_path,20)
    
        # Define the text to display
        text ="hello deer"
        
        # Position to draw the text
        text_x = 20
        text_y = 50
        
        # Draw the text on the canvas
        draw.text((text_x, text_y),text,font=txt_font,fill=0)
        
        # Display the image on the e-Paper display
        epd.display_Fast(epd.getbuffer(canvas))
        time.sleep(10)
        epd.Clear()

    except KeyboardInterrupt:    
        logging.info("ctrl + c:")
        epd2in7_V2.epdconfig.module_exit(cleanup=True)
        exit()

main()
