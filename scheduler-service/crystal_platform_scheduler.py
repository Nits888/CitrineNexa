import datetime
import os
import json

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
import modules.database_operations as db_ops
from globals import logger

# Read environment from SERVERENV environment variable
env = os.environ.get('SERVERENV')
if not env:
    logger.error("SERVERENV environment variable not set.")
    raise EnvironmentError("SERVERENV environment variable not set.")

# Check if DB_ENABLED flag is set
db_enabled = os.environ.get('DB_ENABLED', 'False').lower() == 'true'

# Load scheduler configuration from JSON file
config_path = os.path.join('config', env, 'schedule_config.json')
try:
    with open(config_path, 'r') as file:
        tasks = json.load(file)
except FileNotFoundError:
    logger.error(f"Scheduler configuration file not found for environment: {env}")
    raise FileNotFoundError(f"Scheduler configuration file not found for environment: {env}")

# Instantiate the BlockingScheduler
scheduler = BlockingScheduler()


def execute_task(command):
    """
    Execute the given command, update the database with the execution status if DB_ENABLED is set,
    and always append the execution details to the JSON file.

    :param command: The command to be executed.
    """
    status = "Success"
    logs = None

    try:
        os.system(command)
    except Exception as e:
        logger.error(f"Failed to execute task {command}: {e}")
        status = "Fail"
        logs = str(e)

    # Append to the JSON file
    execution_detail = {
        "command": command,
        "execution_time": datetime.datetime.now().isoformat(),
        "status": status,
        "logs": logs
    }
    with open('execution_history.json', 'a+') as exec_file:
        exec_file.seek(0)
        data = exec_file.read(100)
        if len(data) > 0:
            exec_file.write(",\n")
        json.dump(execution_detail, exec_file)

    # If DB_ENABLED is set, update the database
    if db_enabled:
        task_id = db_ops.insert_scheduled_task(command)
        db_ops.update_execution_status(task_id, status, logs)

    # Rollover after appending to the JSON file
    rollover_execution_history()


def write_execution_history_to_json():
    """
    If DB_ENABLED is set, fetch the execution history for the last 15 days from the database
    and write it to the JSON file.
    """
    if db_enabled:
        history = db_ops.fetch_execution_history()
        with open('execution_history.json', 'w') as wr_file:
            json.dump(history, wr_file, indent=4)

    # Rollover after appending to the JSON file
    rollover_execution_history()


def rollover_execution_history():
    """
    Ensure that the execution_history.json file only contains the latest 15 days of data.
    Remove entries older than 15 days.
    """
    with open('execution_history.json', 'r') as roll_file:
        data = json.load(roll_file)

    # Filter out entries older than 15 days
    cutoff_date = datetime.datetime.now() - datetime.timedelta(days=15)
    updated_data = [entry for entry in data if datetime.datetime.fromisoformat(entry["execution_time"]) >= cutoff_date]

    # Write the updated data back to the file
    with open('execution_history.json', 'w') as roll_file:
        json.dump(updated_data, roll_file, indent=4)


# Schedule tasks based on the configuration
for task in tasks:
    trigger = CronTrigger.from_crontab(task["cron"])
    scheduler.add_job(execute_task, trigger=trigger, args=[task["command"]])

if __name__ == "__main__":
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        # Shut down the scheduler gracefully
        scheduler.shutdown()
