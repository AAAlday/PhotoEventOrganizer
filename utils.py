import sys
from os import path
from re import sub

def getResourcePath(relativePath):
        if hasattr(sys, '_MEIPASS'):
            return path.join(sys._MEIPASS, relativePath) # _MEIPASS is hardcoded internal variable used by Pyinstaller's bootloader
        else:
            return path.join(path.abspath("."), relativePath)

def sanitizeText(textToBeSanitized):
     return sub("/", "∕", textToBeSanitized) # Substitutes normal slashes with division slashes