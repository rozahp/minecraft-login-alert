#!/usr/bin/env python
##
## Filename:    minecraft-login-alert.py
##
## Description: tracks minecraft log and send alerts if someone logins.
##

DEBUG=False

import atexit
import os
import SocketServer
from daemon import runner
#import runner
from datetime import datetime
from collections import defaultdict

##
## Import project classes and variables
##
from alerter import Alerter
from globals import *
from handler import Handler

##=============================
##
## MinecraftLoginAlertDaemon
##
##=============================
class MinecraftLoginAlertDaemon():
    """Daemon runner for detaching process from terminal"""

    def __init__(self):
        self.CONFIG = self.read_configfile()
        self.logdir = self.CONFIG['logdir']
        self.logfiletowatch = self.CONFIG['logfiletowatch']
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/tty'
        self.stdout_path = self.logdir+"/stdout.log"
        self.stderr_path = '/dev/tty'
        self.stderr_path = self.logdir+"/stderr.log"
        self.pidfile_path = self.CONFIG['pidfile']
        self.pidfile_timeout = 5
        #
        # Error check
        #
        if not os.path.exists(self.logdir):
            print "Err: LOGDIR does not exist - please check system/configfile."
            exit(-1)

    ##
    ## Read Configfile
    ##
    def read_configfile(self):
        """Read Configfile and return dict with CONFIG"""

        #
        # Parse configfile
        #
        filename=CONFIGFILE
        try:
            fp=open(filename,"r")
            if DEBUG: print "Log: reading configurations from:", filename
        except:
            try:
                fp=open('/etc/'+filename,"r")
                if DEBUG: print "Log: reading configurations from:", '/etc/'+filename
            except:
                print "Err: did not find configuration file:", filename
                print "Err: please check documentations."
                exit(-1)
            filename='/etc/'+filename

        CONFIG={}
        for row in fp.readlines():
            #
            # Check For Comments
            #
            if "#" == row[0] or '[' == row[0]: continue

            #
            # CONFIG
            #
            if '=' in row:
                row=row.strip().split()[0].split('=')
                if len(row)!=2:
                    print "Err: bad row in configuration file:", filename, "row:", row
                    exit(-1)
                key=row[0].lower()
                value=row[1]
                if key not in CONFIG_PARTS:
                    print "Err: unknown configuration key in file:", filename, "row:", row
                    exit(-1)

                if key in CONFIG and not key == 'watchword' and not key == 'donotalert': 
                    print "Err: key already set in configuration file:", filename, "row:", row, "last config:", CONFIG[key]
                    exit(-1)
                if len(value)==0:
                    print "Err: value has no length in configuration file:", filename, "row:", row
                if key == 'watchword' or key == 'donotalert':
                    if key in CONFIG:
                        CONFIG[key].append(value)
                    else:
                        CONFIG[key]=[]
                        CONFIG[key].append(value)
                else: CONFIG[key]=value
            #
            # Else Error
            #
            else:
                print "Err: bad row in configuration file:", filename, "row:", row
                exit(-1)
        #
        # Close File
        #
        fp.close()
        #
        # Error Check CONFIG
        #
        if all(key in CONFIG for key in CONFIG_PARTS)!=True:
            print "Err: missing key in configuration", filename, "keys:", CONFIG_PARTS
            exit(-1)

        #
        # Return
        #
        return CONFIG

    ##
    ## Check Row for hits
    ##
    def check_row(self, row):
        """Check that rows from logfiles are sane"""
        #
        # Check for comments
        #
        if "#" == row[0]: return False
        row=row.strip()
        #
        # Check for headers
        #
        if any(header in row for header in self.CONFIG['watchwords']): return False
        #
        # Get row data
        #
        return row

    ##
    ## If program terminates - dump tracker status to logfile
    ##
    def dump_atexit(self):
        print "Log: exiting - writing current status to logfile."

    ##
    ## Rotate logs
    ##
    def rotate_logs(self):
        """Every midnight rotate logs"""
        now=datetime.now()
        maxdays=int(self.server.CONFIG['maxlogs'])
        logfiles=self.get_logfiles()
        for f in logfiles:
            then=datetime.strptime(f.split(".")[1], "%Y%m%d")
            x=now-then
            #
            # Remove logs older then maxdays
            #
            filename=self.logdir + "/" + f
            if x.days>maxdays: os.remove(filename)

    ##========================
    ##
    ## Daemon runner
    ##
    ##========================

    def run(self):
        """Function which is called from the Daemon runner"""
        print "MinecraftLoginAlertDaemon() Starting ..."
        self.server=Handler()
        #
        # Set current log date
        #
        now = datetime.now()
        self.server.LOG_DATE = now.strftime('%Y%m%d')
        #
        # Set Variables
        #
        self.server.CONFIG=self.CONFIG
        #
        # Instantiate alerter
        #
        alerter=Alerter()
        self.server.alert = alerter.alert
        self.server.logdir = self.logdir
        #
        # Register atexit
        #
        atexit.register(self.dump_atexit)
        #
        # Start UDP handler forever ...
        #
        self.server.run()

##=======================
##
## MAIN
##
##=======================

if __name__ == "__main__":

    app = MinecraftLoginAlertDaemon()
    daemon_runner = runner.DaemonRunner(app)
    daemon_runner.do_action()

##
## EOF
##
