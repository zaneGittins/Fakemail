import re
import subprocess
from helpers import Logging

class DNSDiverter:

    def __init__(self,dns_ip):
        self.dns_ip = dns_ip
        self.log_file = "dns-diverter"
        self.get_interfaces()

    def get_interfaces(self):
        netshcmd=subprocess.Popen('netsh interface ip dump', shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE )
        output, errors =  netshcmd.communicate()
        if errors:
            Logging.log(str(errors),self.log_file)
        interfaces = re.findall('\"(.+?)\"', str(output))
        self.interfaces = interfaces

    def divert_interfaces(self):
        for interface in self.interfaces:
            netsh = 'netsh interface ip set dns name="' + interface + '" static 127.0.0.1'
            netshcmd=subprocess.Popen(netsh, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE )
            output, errors =  netshcmd.communicate()
            if errors:
                Logging.log(str(errors),self.log_file)
            else:
                Logging.log(("DNS for " + interface + " set to 127.0.0.1"),self.log_file)

    def restore_interfaces(self):
        for interface in self.interfaces:
            netsh = 'netsh interface ip set dns name="' + interface + '" dhcp'
            netshcmd=subprocess.Popen(netsh, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE )
            output, errors =  netshcmd.communicate()
            if errors:
                Logging.log(str(errors),self.log_file)
            else:
                Logging.log(("DNS for " + interface + " dhcp"),self.log_file)