#!/usr/bin/env python

import os, commands, random
os.system('get-sentense-me.sh')
directory = commands.getoutput('find '+ os.environ['HOME'] + '/Pictures/sentense.me/wallpapers -iname *.png')

directory = directory.split('\n')

selection = random.randrange(0, len(directory), 1)

os.system('gconftool-2 -t str -s /desktop/gnome/background/picture_filename ' + str(directory[selection]))

