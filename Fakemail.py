#!/usr/bin/env python3
# FAKEMAIL
# Author: Zane Gittins (@0wlSec)
# Date: 4/22/2020
# netsh interface ip set dns name="Local Area Connection" static 4.2.2.2

import sys
import argparse
import subprocess
import threading
import time
from signal import signal, SIGINT
from listeners import DNSListener
from listeners import SMTPListener
from helpers import Diverter

dns_diverter = None

def handler(signal_received, frame):
    dns_diverter.restore_interfaces()
    print('Shutting down...')
    exit(0)

if __name__ == "__main__":

    signal(SIGINT, handler)

    banner = '''
    ______ ___   _   __ ________  ___  ___  _____ _     
    |  ___/ _ \\ | | / /|  ___|  \\/  | / _ \\|_   _| |    
    | |_ / /_\\ \\| |/ / | |__ | .  . |/ /_\\ \\ | | | |    
    |  _||  _  ||    \\ |  __|| |\\/| ||  _  | | | | |    
    | |  | | | || |\\  \\| |___| |  | || | | |_| |_| |____
    \\_|  \\_| |_/\\_| \\_/\\____/\\_|  |_/\\_| |_/\\___/\\_____/
    Author: Zane Gittins (@0wlSec)
    '''

    print(banner)
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--listen", "-l", help="Address to listen at.")
    parser.add_argument("--port", "-p", help="Port to listen on.")
    parser.add_argument("--dns", "-d", help="DNS port for server to listen on.")
    args = parser.parse_args()

    if(args.listen and args.port):

        print("[+] SMTP Listening at " + args.listen + ":" + args.port)
        smtp_server = SMTPListener.SMTPServer(args.listen, int(args.port))
        smtp_thread = threading.Thread(target=smtp_server.start)
        smtp_thread.daemon = True
        smtp_thread.start()

        if(args.dns):
            print("[+] DNS Listening at " + args.listen + ":" + args.dns)
            dns_server = DNSListener.DNSServer(args.listen, int(args.dns))
            dns_thread = threading.Thread(target=dns_server.start)
            dns_thread.daemon = True
            dns_thread.start()

            dns_diverter = Diverter.DNSDiverter('127.0.0.1')
            dns_diverter.divert_interfaces()
       
    else:
        print(parser.print_help())
        
    while(True):
        time.sleep(1)