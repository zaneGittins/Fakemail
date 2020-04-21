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

Differences from FAKENET:
    * Only for SMTP traffic. 
    * Captures SMTP credentials.

## Credits

Ideas and code inspired and copied from these projects:

* [Fakenet-NG](https://github.com/fireeye/flare-fakenet-ng)
* [WhiteDNS](https://github.com/Dave-ee/WhiteDNS)