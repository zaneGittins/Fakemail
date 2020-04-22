import time

def log(message, logname):
    if message[-1:] != "\n":
        message += "\n"

    log_file = open(logname,"a+")
    current_time = str(time.strftime('%Y-%m-%d %H:%M:%S'))
    to_log = (current_time + " -- " + message)
    print(to_log)
    log_file.write(to_log)
    log_file.close()