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

CREATE TABLE currencies (
    id SERIAL PRIMARY KEY,
    code TEXT UNIQUE NOT NULL
);

CREATE TABLE deposits (
    id SERIAL PRIMARY KEY,
    depositor_id INTEGER NOT NULL REFERENCES depositors (id),
    currency_id INTEGER NOT NULL REFERENCES currencies (id),
    status TEXT NOT NULL,
    amount NUMERIC(15, 2) NOT NULL,
    interest_rate NUMERIC(5, 2) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    created_by INTEGER REFERENCES users (id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX deposits_created_at_index ON deposits (created_at DESC);
CREATE INDEX deposits_depositor_id_index ON deposits (depositor_id);
CREATE INDEX deposits_status_index ON deposits (status);

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

INSERT INTO currencies (code) VALUES
    ('USD'),
    ('EUR'),
    ('RUB');
