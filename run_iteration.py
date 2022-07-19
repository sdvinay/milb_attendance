import os
import time
import logging
import scrape_attendance as sa

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')

# configuration for the remote location
REMOTE_USER='u35698910'
REMOTE_HOST='home92388257.1and1-data.host'
REMOTE_DIR='kumars/vinay/milb_attendance_data'

NUM_LOOPS=1000
SLEEP_INTERVAL=10

for i in range(NUM_LOOPS):
    logging.info(f'Starting iteration {i}')
    sa.main()
    local_dir_listing = os.popen('ls -ltr output').read()  # see the local output
    logging.info(local_dir_listing)
    rsync_output = os.popen(f'rsync -ahzi output/ {REMOTE_USER}@{REMOTE_HOST}:{REMOTE_DIR}').read() # sync
    logging.info(rsync_output)
    # ssh ${REMOTE_USER}@${REMOTE_HOST} ls -ltr ${REMOTE_DIR} # see the remote output
    # echo `date` Finished iteration $i

    # # sleep (unless we're on the last iteration)
    if i < NUM_LOOPS:
        os.system(f'echo sleeping {SLEEP_INTERVAL} seconds')
        time.sleep(SLEEP_INTERVAL)

