##
## Filename: handler.py
##
## Description: handler class for watching minecraft logfile for logins
##

DEBUG=False

import os
import sys
import time
from datetime import datetime
from geoip import geolite2
##
## Import project variables
##

from globals import *

##=================================
##
## Handler Class
##
##=================================
class Handler():
    """Handle Server"""
    def __init__(self):
        self.logdir=False
        self.LOG_DATE = False
        self.CONFIG=False
        self.alert = False
        self.logdir = False
        self.rotate_logs = False
    ##
    ## Set time
    ##
    def set_time(self):
        """Set date and time"""
        now = datetime.now()
        self.current_date = now.strftime("%Y%m%d")
        self.current_time = now.strftime("%H%M")
        
    ##
    ## Dump error
    ##
    def dump_err(self, error):
        """Log errors to file"""
        filename=self.logdir+"/"+ERRFILE_PREFIX+"."+str(self.LOG_DATE)+"."+LOGFILE_SUFFIX
        if DEBUG: print "Dumping error to file:", filename
        try:
            with open(filename,"a") as f:
                    f.write(str(self.current_date))
                    f.write(":")
                    f.write(str(self.current_time))
                    f.write(":")
                    f.write(error)
                    f.write('\n')

        except Exception as err:
            if DEBUG: print "Err: error while opening file:", str(err)
            exit(-1)
    ##
    ## Dump alert
    ##
    def dump_alert(self, alert):
        """Log alerts to file"""
        filename=self.logdir+"/"+ALERTFILE_PREFIX+"."+str(self.LOG_DATE)+"."+LOGFILE_SUFFIX
        if DEBUG: print "Dumping alert to file:", filename
        try:
            with open(filename,"a") as f:
                f.write("Date: "+self.current_date+"|Time: "+self.current_time+"|Alert: ")
                f.write(str(alert)+'\n')

        except Exception as err:
            if DEBUG: print "Err: error while opening file:", err
            exit(-1)

    ##
    ## Check new date
    ##
    def check_new_date(self):
        """Check if date has changed, then rotate logfile and reset tracker"""
        if self.LOG_DATE != self.current_date:
            #
            # Dump tracker dictionary to file
            #
            self.rotate_logs()
            self.LOG_DATE = self.current_date
    ##
    ## Fix Row
    ##
    def fixrow(self, row):
        newrows=[]
        try:
            user, ip = row.split(']')[2].split(' ')[1].split('[/')
            if user in self.CONFIG["donotalert"]:
                return False
            ip=ip.split(':')[0]
            match=geolite2.lookup(ip)
            if match is None:
                country="Not found"
            else:
                country=match.country
            newrows=[   "User:    "+user,
                        "IP:      "+ip.split(':')[0],
                        "Country: "+country]
        except Exception as orsak:
            return "Err: error while extracting user and ip address from row: "+row+"|"+str(orsak)
        return newrows
    ##=========================================
    ##
    ## Run is called from Daemon Process
    ##
    ##=========================================
    def run(self):
        """handle() is called from Daemon Process"""
        #
        # Update time
        #
        self.set_time()
        #
        # Error catcher
        #
        try:
            name = self.CONFIG['logfiletowatch']
            current = open(name, "r")
            curino = os.fstat(current.fileno()).st_ino
            buf=current.readlines()
            while True:
                while True:
                    buf = current.readlines()
                    if len(buf) == 0: break
                    for row in buf:
                        if any(x in row.lower() for x in self.CONFIG['watchword']):
                            newrow=self.fixrow(row)
                            if newrow:
                                self.alert(newrow)
                                self.dump_alert(newrow)
                            if DEBUG:
                                sys.stdout.write(row)
                                sys.stdout.flush()
                time.sleep(SLEEP)
                try:
                    if os.stat(name).st_ino != curino:
                        new = open(name, "r")
                        current.close()
                        current = new
                        curino = os.fstat(current.fileno()).st_ino
                        continue
                except Exception:
                    pass
                time.sleep(SLEEP)
                #
                # Check if new date, then rotate logfiles
                #
                self.set_time()
                self.check_new_date()
        #
        # Exception handler
        #
        except Exception as err:
            error="Err: exception occurred in handle(): "+str(err)
            if DEBUG: print error
            self.dump_err(error)

##
## EOF
##
