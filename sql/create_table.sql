CREATE TABLE IF NOT EXISTS execution_history (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    command TEXT NOT NULL,
    execution_time TIMESTAMP NOT NULL,
    status VARCHAR(50) NOT NULL
);