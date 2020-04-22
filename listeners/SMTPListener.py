import socket
import base64
import time
import threading
from helpers import Logging

class SMTPClientHandler(object):

    def __init__(self, server, connection, address):
        self.server             = server
        self.address            = address
        self.connection         = connection
        self.command            = ""
        self.smtp_commands = ['HELO', 'EHLO', 'MAIL', 'RCPT', 'DATA', 'AUTH', 'NOOP', 'RSET', 'QUIT', 'DATA']
        self.log_file           = "smtp-log"
        
    def connection_send(self, data):
        end_data = "\r\n"
        try:
            
            # Send message to log.
            message = "Sending '" + data + "' to client."
            Logging.log(message,self.log_file)

            # Ensure that data ends with return, newline.
            if data[-2:] != end_data:
                data += end_data

            # Send message to client.
            self.connection.sendall(data.encode("UTF-8"))

        except Exception as e:
            Logging.log(str(e), self.log_file)

    def handle_connection(self):
        
        self.connection_send("220 evilcorp.com Simple Mail Transfer Service Ready")

        while True:
            try:
                self.command  = self.connection.recv(self.server.recv_buffer)
                if not self.command: break
                self.command  = self.command.decode("UTF-8")
                function      = self.command[:4].strip().upper()

                Logging.log(self.command, self.log_file)

                if function in self.smtp_commands:
                    getattr(self, function)()
                else:
                    self.connection_send("503 Command not supported")

            except Exception as e:
                Logging.log(str(e),self.log_file)
                break
        
        self.stop()


    def HELO(self):
        self.connection_send("250-evilcorp.com Hello client.evilcorp.com")
        self.connection_send("250 AUTH LOGIN")

    def EHLO(self):
        self.connection_send("250-evilcorp.com Hello client.evilcorp.com")
        self.connection_send("250 AUTH LOGIN")

    def AUTH(self):
        self.connection_send("334 UGFzc3dvcmQ6")
        username = self.command.split(" ")[2]
        username = base64.b64decode(username).decode("UTF-8") 
        password = self.connection.recv(self.server.recv_buffer)
        password = password.decode("UTF-8")
        password = base64.b64decode(password).decode("UTF-8") 
        Logging.log(("Username: " + username),self.log_file)
        Logging.log(("Password: " + password),self.log_file)
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
        self.connection_send("221 evilcorp.com bye")
    
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
                Logging.log("Breaking recieved end.", self.log_file)
                break

        Logging.log('Received mail data.',self.log_file)
        for line in mail_data.split("\n"):
            Logging.log(line,self.log_file)

        self.connection_send("250 OK")
    
    def stop(self):
        Logging.log('Stopping...',self.log_file)
        self.connection.close()

class SMTPServer:

    def __init__(self, listen_address=None, listen_port=None):
        self.listen_port     = listen_port
        self.listen_address  = listen_address
        self.data_port       = None
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
            smtp_client_thread = threading.Thread(target=smtp_client_handler.handle_connection)
            smtp_client_thread.daemon = True
            smtp_client_thread.start()