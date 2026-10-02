# Periodically it monitors a file and print new lines as they're appended.

import argparse
import os
import time

def tail_f(file_path, time_to_wait):

    # Input validation
    if not os.path.exists(file_path):
        raise FileNotFoundError("The specified file does not exist.")
    if time_to_wait < 0:
        raise ValueError("Time to wait must be greater than or equal to 0.")

    # File is read line by line. in order to avoid loading the whole file in memory.
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
    parser.add_argument("-f", "--file_path", required=True, help="The path to the log file you want to monitor.")
    parser.add_argument("-t", "--time_to_wait", type=int, default=3, help="Seconds to wait between checks (default: 3).")
    
    # Parse the arguments from the command line
    args = parser.parse_args() 
    try:
        print("Monitoring file: " + args.file_path)
        tail_f(args.file_path, args.time_to_wait)
    except KeyboardInterrupt:
        print("Stopped monitoring file: " + args.file_path)
    except FileNotFoundError as e:
        print("Error: " + str(e))
    except ValueError as e:
        print("Error: " + str(e))

    