INSERT INTO execution_history (name, command, execution_time, status)
VALUES (%s, %s, NOW(), 'Scheduled')
RETURNING id;

