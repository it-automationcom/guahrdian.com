#!/usr/bin/python3

import configparser
import os

config=configparser.ConfigParser()
configfile=os.path.dirname(__file__)+'/../config.ini'
config.read(configfile)
output_html=config['dev']['output']
for i in config['rivers']:
    print(i)

