# Periodically it monitors a file and print new lines as they're appended.

import argparse
import os
import time

def tail_f(file_path, time_to_wait):

# First Thing is to read the file. It is read line by line, in order to avoid loading the whole file in memory.

    with open(file_path, "r") as file: 
        # Go at the end  of the file
        file.seek(0, os.SEEK_END)

        while True:
            # Read a line. If it is not empty, print it. Then, wait
            line = file.readline()
            if line: 
                print(line, end="")
            else: 
                time.sleep(time_to_wait)
                        
if __name__=="__main__":   
    parser = argparse.ArgumentParser(description="A custom Python tail -f clone.")
    
    # Arguments to accept
    parser.add_argument("path", help="The path to the log file you want to monitor.")
    parser.add_argument("-t", "--timetowait", type=int, default=3, help="Seconds to wait between checks (default: 3).")
    
    # Parse the arguments from the command line
    args = parser.parse_args() 
    try:
        if not os.path.exists(args.path):
            print ("File does not exist: " + args.path)
        else:
            print("Monitoring file: " + args.path)
            tail_f(args.path, args.timetowait)
    except KeyboardInterrupt:
        print("Exiting tail_f script")