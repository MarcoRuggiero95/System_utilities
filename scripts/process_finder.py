import argparse
import psutil


def process_finder(process_name: str) -> list[tuple[int, float]]:
    if not process_name.strip():
        raise ValueError("Process name must not be empty.")

    matches = []
    for process in psutil.process_iter(["name"]):
        try:
            if process.info["name"] == process_name:
                memory_mb = process.memory_info().rss / (1024 * 1024)
                matches.append((process.pid, memory_mb))
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return matches

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Find running processes by name and report their memory usage."
    )
    parser.add_argument(
        "-p", "--process-name", required=True,
        help="Name of the process to find.",
    )
    args = parser.parse_args()

    try:
        results = process_finder(args.process_name)
    except ValueError as error:
        parser.error(str(error))

    if results:
        for pid, memory_mb in results:
            print(f"PID: {pid}, Memory Usage: {memory_mb:.2f} MB")
    else:
        print(f"No processes found matching {args.process_name!r}.")