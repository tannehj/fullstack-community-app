CREATE TABLE IF NOT EXISTS login_rate_limits (
    bucket_type VARCHAR(16) NOT NULL,
    bucket_key CHAR(64) NOT NULL,
    window_started_at TIMESTAMPTZ NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    attempt_count INTEGER NOT NULL,
    CONSTRAINT login_rate_limits_bucket_type_check
        CHECK (bucket_type IN ('account', 'ip')),
    CONSTRAINT login_rate_limits_attempt_count_check
        CHECK (attempt_count > 0),
    PRIMARY KEY (bucket_type, bucket_key)
);

CREATE INDEX IF NOT EXISTS login_rate_limits_expires_at_idx
    ON login_rate_limits (expires_at);
