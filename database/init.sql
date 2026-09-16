CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
);

CREATE TABLE countries (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE depositors (
    id SERIAL PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    date_of_birth DATE NOT NULL,
    country_id INTEGER NOT NULL REFERENCES countries (id),
    passport TEXT NOT NULL,
    tin TEXT NOT NULL,
    phone TEXT NOT NULL,
    email TEXT NOT NULL,
    address TEXT NOT NULL,
    created_by INTEGER REFERENCES users (id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX depositors_created_at_index ON depositors (created_at DESC);
CREATE INDEX depositors_country_id_index ON depositors (country_id);

INSERT INTO countries (name) VALUES
    ('Australia'),
    ('Austria'),
    ('Belgium'),
    ('Brazil'),
    ('Canada'),
    ('China'),
    ('Denmark'),
    ('Finland'),
    ('France'),
    ('Germany'),
    ('Greece'),
    ('India'),
    ('Ireland'),
    ('Italy'),
    ('Japan'),
    ('Mexico'),
    ('Netherlands'),
    ('Norway'),
    ('Poland'),
    ('Portugal'),
    ('Singapore'),
    ('Spain'),
    ('Sweden'),
    ('Switzerland'),
    ('Turkey'),
    ('United Kingdom'),
    ('United States');
