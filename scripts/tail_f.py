# Periodically it monitors a file and print new lines as they're appended.

import argparse
import os
import time
from collections import deque


def tail_f(file_paths, time_to_wait, number_of_lines=0):
    if isinstance(file_paths, (str, os.PathLike)):
        file_paths = [os.fspath(file_paths)]
    else:
        file_paths = [os.fspath(path) for path in file_paths]

    if not file_paths:
        raise ValueError("At least one file path is required.")
    if number_of_lines < 0:
        raise ValueError("Number of lines must be greater than or equal to 0.")
    if time_to_wait <= 0:
        raise ValueError("Time to wait must be greater than 0.")

    for path in file_paths:
        if not os.path.isfile(path):
            raise FileNotFoundError(f"The specified file does not exist: {path}")

    states = {}
    try:
        for path in file_paths:
            file = open(path, "r")
            if number_of_lines:
                initial_lines = deque(file, maxlen=number_of_lines)
                if initial_lines:
                    print(f"Monitoring {os.path.basename(path)}:")
                    print("".join(initial_lines), end="")
            file.seek(0, os.SEEK_END)
            file_stat = os.fstat(file.fileno())
            states[path] = {
                "file": file,
                "identity": (file_stat.st_dev, file_stat.st_ino),
                "position": file.tell(),
            }

        while True:
            for path in file_paths:
                try:
                    path_stat = os.stat(path)
                    identity = (path_stat.st_dev, path_stat.st_ino)
                    state = states[path]
                    if identity != state["identity"]:
                        state["file"].close()
                        file = open(path, "r")
                        file_stat = os.fstat(file.fileno())
                        state.update(
                            file=file,
                            identity=(file_stat.st_dev, file_stat.st_ino),
                            position=0,
                        )

                    file = state["file"]
                    if path_stat.st_size < state["position"]:
                        file.seek(0)

                    line = file.readline()
                    if line:
                        print(f"Monitoring {os.path.basename(path)}:")
                        while line:
                            print(line, end="")
                            line = file.readline()
                    state["position"] = file.tell()
                except OSError:
                    # The path may be temporarily unavailable during rotation.
                    continue
            time.sleep(time_to_wait)
    finally:
        for state in states.values():
            state["file"].close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A custom Python tail -f clone.")

    parser.add_argument(
        "-f", "--file_path", "--file-path", nargs="+", required=True,
        help="One or more files to monitor.",
    )
    parser.add_argument(
        "-n", "--lines", type=int, default=0,
        help="Number of existing lines to display (default: 0).",
    )
    parser.add_argument(
        "-t", "--time_to_wait", "--time-to-wait", type=float, required=True,
        help="Seconds to wait between checks.",
    )
    args = parser.parse_args()

    try:
        tail_f(args.file_path, args.time_to_wait, args.lines)
    except KeyboardInterrupt:
        print("Monitoring stopped.")
    except (FileNotFoundError, ValueError) as error:
        parser.error(str(error))

