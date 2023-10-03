CREATE TABLE IF NOT EXISTS execution_history (
    id SERIAL PRIMARY KEY,
    command TEXT NOT NULL,
    execution_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    update_time TIMESTAMP,
    status TEXT NOT NULL,
    logs TEXT
);
