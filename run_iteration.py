import os
import time
import logging
import typer
import scrape_attendance as sa

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')

# configuration for the remote location
REMOTE_USER='u35698910'
REMOTE_HOST='home92388257.1and1-data.host'
REMOTE_DIR='kumars/vinay/milb_attendance_data'

NUM_LOOPS_DEFAULT=1000
SLEEP_INTERVAL_DEFAULT=3600

def run_shell_command(cmd: str):
    logging.info(f'Running shell command: {cmd}')
    output = os.popen(cmd).read()
    logging.info(output)
    return output

def run_iteration(i: int):
    logging.info(f'Starting iteration {i}')
    sa.main()
    run_shell_command('ls -ltr output') # see the local output
    run_shell_command(f'rsync -ahzi output/ {REMOTE_USER}@{REMOTE_HOST}:{REMOTE_DIR}')  # sync
    run_shell_command(f'ssh {REMOTE_USER}@{REMOTE_HOST} ls -ltr {REMOTE_DIR}') # see the remote output
    logging.info(f'Finished iteration {i}')


def main(num_loops: int = NUM_LOOPS_DEFAULT, sleep_interval: int = SLEEP_INTERVAL_DEFAULT):
    logging.info(f'Script starting a run of {num_loops} iterations with a sleep interval of {sleep_interval}')
    for i in range(num_loops):
        run_iteration(i)
        # sleep (unless we're on the last iteration)
        if i+1 < num_loops:
            logging.info(f'sleeping {sleep_interval} seconds')
            time.sleep(sleep_interval)

if __name__ == "__main__":
    typer.run(main)  # Allow overrides with --num-loops or --sleep-interval
