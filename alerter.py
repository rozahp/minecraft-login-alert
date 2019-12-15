##
## Filename:  alerter.py
##
## Description: Alerter class for LogFileTracker
##

DEBUG=False

from globals import *
import hashlib
import urllib3
from matrix_client.api import MatrixHttpApi
import json

##=================================
##
## Alerter Class
##
##=================================
class Alerter:
    """
    Barebone alerter class for LogFileTracker
    Write your own and import it into this file
    """
    def __init__(self):
        pass
    #
    # Alert
    #
    def alert(self, message):
        """
        Alert message received from the MinecraftLoginAlertDaemon()
        when a logline is found to match a watch word.
        Message is the logline.
        """
        if DEBUG: 
            print "Alerter got message:", message
            for f in message:
                print "Alert: "+f

##
## EOF
##
