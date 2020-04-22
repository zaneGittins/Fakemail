import time

def log(message, logname):    
    log_file_name = logname + ".txt"
    log_file = open(log_file_name,"a+")
    current_time = str(time.strftime('%Y-%m-%d %H:%M:%S'))
    to_log = ("[" + logname + "][" + current_time + "]: " + message)
    print(to_log)
    if to_log[-1:] != "\n":
        to_log += "\n"
    log_file.write(to_log)
    log_file.close()