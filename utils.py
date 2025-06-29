import sys
from os import path

def getResourcePath(relativePath):
        if hasattr(sys, '_MEIPASS'):
            return path.join(sys._MEIPASS, relativePath) # _MEIPASS is hardcoded internal variable used by Pyinstaller's bootloader
        else:
            return path.join(path.abspath("."), relativePath)