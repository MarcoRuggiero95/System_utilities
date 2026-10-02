# A script that checks disk usage on PATH and prints a warning if usage is above a Threshold. 

import os
import argparse
import shutil

def disk_usage_alert(path, threshold=80):

    if threshold < 0 or threshold > 100:
        raise ValueError("Threshold must be between 0 and 100.")

    if not os.path.exists(path):
        raise ValueError("The specified path does not exist.")

    # usage returns multiple values.    
    usage = shutil.disk_usage(path)

    used = usage.used
    total = usage.total

    percentage_used = (used/total) * 100

    if percentage_used >= threshold:
        print("Warning: Disk usage is " + str(round(percentage_used,2)) + "%")

if __name__=="__main__":
    parser = argparse.ArgumentParser(description="A script that checks disk usage on PATH and prints a warning if usage is above a Threshold.")
    
    # Arguments to accept
    parser.add_argument("-p", "--path", default="/", help="The path to check disk usage for.")
    parser.add_argument("-t", "--threshold", type=int, default=80, help="Disk usage percentage threshold (default: 80).")
    
    # Parse the arguments from the command line
    args = parser.parse_args() 

    try: 
        disk_usage_alert(args.path, args.threshold)
    except ValueError as e:
        print("Error: " + str(e))
