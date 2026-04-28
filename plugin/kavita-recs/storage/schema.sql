CREATE TABLE IF NOT EXISTS series_cache (
    series_id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    summary TEXT,
    format TEXT,
    genres_json TEXT,
    tags_json TEXT,
    writers_json TEXT,
    release_year INTEGER,
    page_count INTEGER,
    read_time_minutes INTEGER,
    want_to_read INTEGER DEFAULT 0,
    user_rating REAL,
    external_rating REAL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS progress_cache (
    series_id INTEGER PRIMARY KEY,
    status TEXT NOT NULL,
    percent REAL,
    last_read_at TEXT,
    current_chapter_id INTEGER,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS recommendation_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    requested_at TEXT NOT NULL,
    request_text TEXT,
    constraints_json TEXT NOT NULL,
    candidate_ids_json TEXT NOT NULL,
    result_json TEXT NOT NULL,
    accepted INTEGER
);

CREATE TABLE IF NOT EXISTS feedback_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    series_id INTEGER NOT NULL,
    feedback_type TEXT NOT NULL,
    feedback_reason TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS preference_features (
    feature_key TEXT NOT NULL,
    feature_scope TEXT NOT NULL,
    feature_value TEXT NOT NULL,
    weight REAL NOT NULL,
    updated_at TEXT NOT NULL,
    expires_at TEXT,
    PRIMARY KEY (feature_key, feature_scope)
);

CREATE TABLE IF NOT EXISTS daily_state (
    state_date TEXT PRIMARY KEY,
    energy_estimate TEXT,
    available_minutes INTEGER,
    notes TEXT
);
