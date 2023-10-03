INSERT INTO execution_history (name, command, status) VALUES (%s, %s, 'Scheduled') RETURNING id;
