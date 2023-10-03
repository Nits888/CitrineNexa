import json
import os
import psycopg2
from psycopg2 import pool

from globals import env, logger

# Check if DB_ENABLED flag is set
db_enabled = os.environ.get('DB_ENABLED', 'False').lower() == 'true'

if db_enabled:
    # Load database configuration from JSON file
    config_path = os.path.join('config', env, 'database_config.json')
    try:
        with open(config_path, 'r') as file:
            db_config = json.load(file)
    except FileNotFoundError:
        logger.error(f"Database configuration file not found for environment: {env}")
        raise FileNotFoundError(f"Database configuration file not found for environment: {env}")

    # Initialize DML connection pool
    dml_pool = pool.SimpleConnectionPool(
        2, 5,
        dbname=db_config["database"],
        user=db_config["dml_user"],
        password=os.environ.get('DMLINFO'),
        host=db_config["server"],
        port=db_config["port"]
    )
else:
    dml_pool = None


def connect_ddl():
    """
    Establish a direct connection using the DDL user credentials.

    :return: A psycopg2 connection object or None if connection fails.
    """
    try:
        conn = psycopg2.connect(
            dbname=db_config["database"],
            user=db_config["ddl_user"],
            password=os.environ.get('DDLINFO'),
            host=db_config["server"],
            port=db_config["port"]
        )
        return conn
    except Exception as e:
        logger.error(f"Failed to connect to database using DDLINFO: {e}")
        return None


def read_sql_file(filename):
    """
    Read SQL query from a file.

    :param filename: Name of the SQL file.
    :return: SQL query as a string.
    """
    with open(os.path.join('sql', filename), 'r') as read_file:
        return read_file.read()


def initialize_table():
    """
    Check and create the execution_history table if it doesn't exist.
    """
    conn = connect_ddl()
    if not conn:
        return

    cursor = conn.cursor()
    try:
        cursor.execute(read_sql_file('create_table.sql'))
        conn.commit()
    except Exception as e:
        logger.error(f"Failed to create table: {e}")
    finally:
        cursor.close()
        conn.close()


def insert_scheduled_task(task, command):
    """
    Insert a new scheduled task into execution history with status "Scheduled".

    :param task: Task Name
    :param command: The command to be executed.
    :return: The ID of the inserted row.
    """
    conn = dml_pool.getconn()
    cursor = conn.cursor()
    try:
        cursor.execute(read_sql_file('insert_scheduled_task.sql'), (task, command,))
        conn.commit()
        return cursor.fetchone()[0]
    except Exception as e:
        logger.error(f"Failed to insert scheduled task: {e}")
    finally:
        cursor.close()
        dml_pool.putconn(conn)


def update_execution_status(task_id, status):
    """
    Update the status of a task in execution history.

    :param task_id: The ID of the task to be updated.
    :param status: The new status of the task.
    """
    conn = dml_pool.getconn()
    cursor = conn.cursor()
    try:
        cursor.execute(read_sql_file('update_execution_status.sql'), (status, task_id))
        conn.commit()
    except Exception as e:
        logger.error(f"Failed to update execution status: {e}")
    finally:
        cursor.close()
        dml_pool.putconn(conn)



def fetch_execution_history():
    """
    Fetch the execution history and logs for the last 15 days.

    :return: A list of dictionaries containing execution details.
    """
    conn = dml_pool.getconn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT id, command, execution_time, update_time, status, logs
            FROM execution_history
            WHERE execution_time >= NOW() - INTERVAL '15 days'
            ORDER BY execution_time DESC;
        """)
        records = cursor.fetchall()
        return [{
            "id": row[0],
            "command": row[1],
            "execution_time": row[2].isoformat(),
            "update_time": row[3].isoformat() if row[3] else None,
            "status": row[4],
            "logs": row[5]
        } for row in records]
    except Exception as e:
        logger.error(f"Failed to fetch execution history: {e}")
        return []
    finally:
        cursor.close()
        dml_pool.putconn(conn)


if db_enabled:
    # Call the initialize_table function to ensure table exists
    initialize_table()