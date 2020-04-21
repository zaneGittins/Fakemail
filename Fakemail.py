#!/usr/bin/env python3
# FAKEMAIL
# Author: Zane Gittins (@0wlSec)
# Date: 4/21/2020

import socket
import time
import threading
import base64
import argparse
import subprocess
from signal import signal, SIGINT
import sys

smtp_server = None

def handler(signal_received, frame):
    print('Shutting down...')
    smtp_server.stop()
    exit(0)

def log(message, logname):
    if message[-1:] != "\n":
        message += "\n"

    log_file = open(logname,"a+")
    current_time = str(time.strftime('%Y-%m-%d %H:%M:%S'))
    to_log = (current_time + " -- " + message)
    print(to_log)
    log_file.write(to_log)
    log_file.close()

class SMTPClientHandler(object):

    def __init__(self, server, connection, address):
        self.server             = server
        self.address            = address
        self.connection         = connection
        self.command            = ""
        self.smtp_commands = ['HELO', 'EHLO', 'MAIL', 'RCPT', 'DATA', 'AUTH', 'NOOP', 'RSET', 'QUIT', 'DATA']
        self.log_file           = "smtp-log.txt"
        
    def connection_send(self, data):
        end_data = "\r\n"
        try:
            
            # Send message to log.
            message = "Sending '" + data + "' to client."
            log(message,self.log_file)

            # Ensure that data ends with return, newline.
            if data[-2:] != end_data:
                data += end_data

            # Send message to client.
            self.connection.sendall(data.encode("UTF-8"))

        except Exception as e:
            log(str(e), self.log_file)
            self.stop()
            pass

    def handle_connection(self):
        
        self.connection_send("220 evil.com Simple Mail Transfer Service Ready")

        while True:
            try:
                self.command  = self.connection.recv(self.server.recv_buffer)
                if not self.command: break
                self.command  = self.command.decode("UTF-8")
                function      = self.command[:4].strip().upper()

                log(self.command, self.log_file)

                if function in self.smtp_commands:
                    getattr(self, function)()
                else:
                    self.connection_send("503 Command not supported")

            except Exception as e:
                log(str(e),self.log_file)
                self.stop()
        
        self.stop()


    def HELO(self):
        self.connection_send("250-smtp.example.com Hello client.example.com")
        self.connection_send("250 AUTH LOGIN")

    def EHLO(self):
        self.connection_send("250-smtp.example.com Hello client.example.com")
        self.connection_send("250 AUTH LOGIN")

    def AUTH(self):
        self.connection_send("334 UGFzc3dvcmQ6")
        username = self.command.split(" ")[2]
        username = base64.b64decode(username).decode("UTF-8") 
        password = self.connection.recv(self.server.recv_buffer)
        password = password.decode("UTF-8")
        password = base64.b64decode(password).decode("UTF-8") 
        log(("Username: " + username),self.log_file)
        log(("Password: " + password),self.log_file)
        self.connection_send("235 Authentication Succeeded")

    def MAIL(self):
        self.connection_send("250 ok")

    def RCPT(self):
        self.connection_send("250 ok")

    def NOOP(self):
        self.connection_send("250 ok")

    def RSET(self):
        self.connection_send("250 ok")

    def QUIT(self):
        self.connection_send("221 evil.com bye")
    
    def DATA(self):
        self.connection_send("354 start mail input, end with <CRLF>.<CRLF>")
        mail_data = ""
        while True:
            mail_data_chunk = self.connection.recv(self.server.recv_buffer)
            mail_data_chunk = mail_data_chunk.decode("UTF-8")

            if not mail_data_chunk:
                break

            mail_data += mail_data_chunk

            if "\r\n.\r\n" in mail_data:
                log("Breaking recieved end.", self.log_file)
                break

        log('Received mail data.',self.log_file)
        for line in mail_data.split("\n"):
            log(line,self.log_file)

        self.connection_send("250 OK")
    
    def stop(self):
        log('Stopping...',self.log_file)
        if self.connection:
            self.connection.close()

class SMTPServer:

    def __init__(self, listen_address=None, listen_port=None):
        self.listen_port     = listen_port
        self.listen_address  = listen_address
        self.data_port       = None
        self.threads         = []
        self.timeout         = 600
        self.recv_buffer     = 4096

    def start(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener = (self.listen_address, self.listen_port)
        sock.bind(listener)
        sock.listen(1)

        while True:

            connection, address = sock.accept()

            smtp_client_handler = SMTPClientHandler(self, connection, address)

            thread = threading.Thread(target=smtp_client_handler.handle_connection)
            thread.start()
            
            self.threads.append((thread, (time.time() + (self.timeout))))

            for thread, timeout in self.threads:
                if time.time() > timeout and thread != None:
                    try:
                        self.threads.remove((thread,timeout))
                        thread.terminate()
                    except Exception:
                        pass
    
    def stop(self):
        for thread, timeout in self.threads:
            self.threads.remove((thread,timeout))
            thread.terminate()
        exit(0)


class DNSClientHandler:

    def __init__(self,data,response_ip):
        self.data = data
        self.response_ip = response_ip
        self.domain = ""

        kind = (data[2] >> 3) & 15
        if kind == 0:
            ini = 12
            lon = data[ini]
            while lon != 0:
                self.domain += str(data[ini+1:ini+lon+1])+"."
                ini += lon + 1
                lon = data[ini]

    def response(self):
        packet = bytearray()
        packet += self.data[:2] + b"\x81\x80"
        packet += self.data[4:6] + self.data[4:6] + b"\x00\x00\x00\x00"
        packet += self.data[12:]
        packet += b"\xc0\x0c"
        packet += b"\x00\x01\x00\x01\x00\x00\x00\x3c\x00\x04"
        packet += bytearray(map(ord,str.join("",map(lambda x: chr(int(x)), self.response_ip.split(".")))))
        return packet

class DNSServer:

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.log_file = "dns-log.txt"
    
    def start(self):
        udp_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_server.bind((self.ip,self.port))

        while True:
            data, addr = udp_server.recvfrom(1024)
            dns_handler = DNSClientHandler(data,'127.0.0.1')
            udp_server.sendto(dns_handler.response(), addr)
            log((f"[+] {dns_handler.domain} -> {self.ip}"),self.log_file)

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
        smtp_server = SMTPServer(args.listen, int(args.port))
        smtp_thread = threading.Thread(target=smtp_server.start)
        smtp_thread.daemon = True
        smtp_thread.start()

        if(args.dns):
            print("[+] DNS Listening at " + args.listen + ":" + args.dns)
            dns_server = DNSServer(args.listen, int(args.dns))
            dns_thread = threading.Thread(target=dns_server.start)
            dns_thread.daemon = True
            dns_thread.start()
       
    else:
        print(parser.print_help())
        
    while(True):
        time.sleep(1)