# Fakemail

Simple fake SMTP and DNS servers.

```
______ ___   _   __ ________  ___  ___  _____ _     
|  ___/ _ \ | | / /|  ___|  \/  | / _ \|_   _| |    
| |_ / /_\ \| |/ / | |__ | .  . |/ /_\ \ | | | |    
|  _||  _  ||    \ |  __|| |\/| ||  _  | | | | |    
| |  | | | || |\  \| |___| |  | || | | |_| |_| |____
\_|  \_| |_/\_| \_/\____/\_|  |_/\_| |_/\___/\_____/
Author: Zane Gittins (@0wlSec)
```

Inspired by FAKENET-NG. Created to help analyze Agent Tesla samples which
often use SMTP for C2.

Since this was build with Agent Tesla in mind, this has only been tested against
.NET SmtpClient, the SMTP server may be unstable for other SMTP clients.

Differences from FAKENET:
* Only for SMTP traffic. 
* Captures SMTP credentials.

## Usage

```powershell
# -l is the address to listen at.
# -p is the port for the SMTP server.
# -d is the port for the DNS server. Not mandatory to start DNS server.
python3 fakemail.py -l 127.0.0.1 -p 25 -d 53
```

## Credits

Ideas and code inspired and copied from these projects:

* [Fakenet-NG](https://github.com/fireeye/flare-fakenet-ng)
* [WhiteDNS](https://github.com/Dave-ee/WhiteDNS)
