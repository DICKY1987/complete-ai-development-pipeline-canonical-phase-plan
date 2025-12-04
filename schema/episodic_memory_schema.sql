CREATE TABLE IF NOT EXISTS episodes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT NOT NULL UNIQUE,
    task_description TEXT NOT NULL,
    user_prompt TEXT NOT NULL,
    files_changed TEXT NOT NULL,
    edit_accepted INTEGER NOT NULL,
    project_conventions TEXT NOT NULL,
    embedding TEXT NOT NULL,
    metadata TEXT,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_episodes_created_at ON episodes(created_at);
