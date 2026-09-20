CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'Active',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_visit_at TIMESTAMPTZ NOT NULL DEFAULT now()
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
    passport TEXT UNIQUE NOT NULL,
    tin TEXT UNIQUE NOT NULL,
    phone TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
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
    amount NUMERIC(15, 2) NOT NULL CHECK (amount > 0),
    interest_rate NUMERIC(5, 2) NOT NULL CHECK (interest_rate BETWEEN 0 AND 100),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    created_by INTEGER REFERENCES users (id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (end_date > start_date)
);

CREATE INDEX deposits_created_at_index ON deposits (created_at DESC);
CREATE INDEX deposits_depositor_id_index ON deposits (depositor_id);
CREATE INDEX deposits_status_index ON deposits (status);
CREATE INDEX deposits_start_date_index ON deposits (start_date);
CREATE INDEX deposits_end_date_index ON deposits (end_date);

CREATE TABLE contracts (
    id SERIAL PRIMARY KEY,
    deposit_id INTEGER NOT NULL UNIQUE REFERENCES deposits (id),
    contract_date DATE NOT NULL,
    signing_status TEXT NOT NULL,
    description TEXT NOT NULL,
    special_conditions TEXT NOT NULL,
    created_by INTEGER REFERENCES users (id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX contracts_created_at_index ON contracts (created_at DESC);
CREATE INDEX contracts_signing_status_index ON contracts (signing_status);

CREATE FUNCTION check_depositor_age() RETURNS trigger AS $$
BEGIN
    IF NEW.date_of_birth > CURRENT_DATE - INTERVAL '18 years' THEN
        RAISE EXCEPTION 'depositor must be at least 18 years old';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER depositors_min_age
    BEFORE INSERT OR UPDATE ON depositors
    FOR EACH ROW
    EXECUTE FUNCTION check_depositor_age();

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
