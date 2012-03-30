#!/usr/bin/env python

import os, commands, random
import time

def change_wallpaper():
    directory = commands.getoutput('find '+ os.environ['HOME'] + '/Pictures/Wallpapers')
    directory = directory.split('\n')
    selection = random.randrange(0, len(directory), 1)
    print str(directory[selection])   
    os.system('gsettings set org.gnome.desktop.background picture-uri "file:' + str(directory[selection]) + '"');

if __name__ == '__main__':
    while True:
        change_wallpaper()
        time.sleep(300)

