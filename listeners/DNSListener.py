import socket
from helpers import Logging

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
                self.domain += (data[ini+1:ini+lon+1]).decode("utf-8")+"."
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
        self.log_file = "dns-log"
    
    def start(self):
        udp_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_server.bind((self.ip,self.port))

        while True:
            data, addr = udp_server.recvfrom(1024)
            dns_handler = DNSClientHandler(data,'127.0.0.1')
            udp_server.sendto(dns_handler.response(), addr)
            Logging.log((f"{dns_handler.domain} -> {self.ip}"),self.log_file)