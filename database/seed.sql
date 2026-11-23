INSERT INTO users (username, email, password_hash) VALUES
    ('admin', 'admin@depositone.com', '$2b$12$sq3UQujkbajA8niMjRb0JuNjqQuYhedmQQZ.hRHhJrMEBlvKPyOgq');

INSERT INTO depositors (first_name, last_name, date_of_birth, country_id, passport, tin, phone, email, address, created_by) VALUES
    ('John', 'Smith', '1985-03-12', 27, 'P1000001', 'T1000001', '+1-202-555-0101', 'john.smith@example.com', '10 Main St, New York', 1),
    ('Emma', 'Brown', '1990-07-25', 26, 'P1000002', 'T1000002', '+44-20-7946-0102', 'emma.brown@example.com', '5 King Rd, London', 1),
    ('Liam', 'Muller', '1978-11-03', 10, 'P1000003', 'T1000003', '+49-30-555-0103', 'liam.muller@example.com', '12 Berliner Str, Berlin', 1),
    ('Olivia', 'Rossi', '1995-01-19', 14, 'P1000004', 'T1000004', '+39-06-555-0104', 'olivia.rossi@example.com', '7 Via Roma, Rome', 1),
    ('Noah', 'Tanaka', '1982-09-30', 15, 'P1000005', 'T1000005', '+81-3-5555-0105', 'noah.tanaka@example.com', '3 Chiyoda, Tokyo', 1);

INSERT INTO deposits (depositor_id, currency_id, status, amount, interest_rate, start_date, end_date, created_by) VALUES
    (1, 1, 'Active', 10000.00, 5.50, '2025-09-20', '2026-09-24', 1),
    (2, 2, 'Active', 25000.00, 4.25, '2026-02-01', '2027-02-01', 1),
    (3, 3, 'Active', 500000.00, 7.00, '2026-01-15', '2026-09-26', 1),
    (4, 1, 'Active', 15000.00, 6.00, '2026-06-01', '2027-06-01', 1),
    (5, 2, 'Pending', 8000.00, 3.50, '2026-09-01', '2027-03-01', 1),
    (1, 1, 'Closed', 5000.00, 4.00, '2024-01-01', '2025-01-01', 1);

INSERT INTO contracts (deposit_id, contract_date, signing_status, description, special_conditions, created_by) VALUES
    (1, '2025-09-18', 'Signed', 'Standard term deposit agreement', 'None', 1),
    (2, '2026-02-01', 'Pending', 'Savings deposit agreement', 'None', 1),
    (4, '2026-06-01', 'Rejected', 'Draft rejected by the depositor', 'None', 1);
