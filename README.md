# MinecraftLoginAlert

This program watches Minecraft logfile and checks for logins. When an user login an alert-function is called (see below about the alerter function).

The alert logfile is rotated every midnight.

Errors are dumped to a logfile (see below).

This program should work on any Linux system with Python 2.7.

## AUTHOR

Phazor / Cascade 1733

## LICENSE

Please feel free to copy, distribute and change this program in any way you like.

## INSTALLATION

1) Install python 2.7

2) virtualenv venv

3) source venv/bin/activate

4) pip -r requirements.txt

5) Edit: minecraft-login-alert.conf

6) Start: python minecraft-login-alert.py start

7) Stop:  python minecraft-login-alert.py stop

Debugging: To enable debugging set DEBUG=True in globals.py.

## CONFIGFILE

Edit macupd_tracker.conf to suit your system.

Example:

    ##
    ## Filename:    minecraft-login-alert.conf
    ##
    ## Description: config file for minecraft-login-alert.py
    ##
    LOGFILETOWATCH=/path/to/minecraft/WORK/logs/latets.log
    LOGDIR=/path/to/where/to/place/logs/logdir
    PIDFILE=/path/to/pidfile/minecraft-login-alert.pid
    MAXLOGS=31    #Remove logs older then 30 days
    ##
    ## WATCHWORDS
    ##
    WATCHWORD=logged in
    ##
    ## DONOTALERT
    ##
    DONOTALERT=Player1
    ##
    ## EOF
    ##


## LOGFILES

There are 2 types of logfiles:

* Alert:   minecraft-login-alert_alert.YYYYMMDD.log - log of alerts.
* Error:   minecraft-login-alert_error.YYYYMMDD.log - log of errors.

## ALERTER

You have to define an alerter function by editing alerter.py. Current file is a barebone class which does nothing. 

The alerter is instantiated by the MinecraftLoginAlertDaemon class and called by the handler when an user login to your minecraft server.

All alerts are logged to file: minecraft-login-alert_alert.YYYYMMDD.log

### Example code

Editing alerter.py:

    from boxcar_class import BoxcarClass # boxcar.io

    class Alerter:
        def __init__(self):
            pass
        def alert(self, message):
            b=BoxcarClass(tokenfile=myboxcar.ini)
            b.title="Minecraft Login Alert"
            b.message=""
            for m in message:
                b.message+=m+'\n'
            b.source="MinecraftLoginAlert"
            b.send()  #Send message via boxcar.io
            del b

## TODO

* Alert on malicious behavior on server
* Alert on ?
