CREATE TABLE users(
    id_users SERIAL PRIMARY KEY,
    email TEXT NOT NULL,
    passwd_auth TEXT NOT NULL,
    creation_date TIMESTAMPTZ NOT NULL,
    validation_date TIMESTAMPTZ NULL,
    is_active BOOLEAN NOT NULL
);


CREATE TABLE scans(
    id_scans SERIAL PRIMARY KEY,
    scan_started TIMESTAMPTZ NOT NULL,
    scan_ended TIMESTAMPTZ NOT NULL,
    file_name TEXT NOT NULL,
    file_bytes_size FLOAT NOT NULL,
    user_id INT NOT NULL REFERENCES Users(id_users)
);

CREATE TYPE mail_types AS ENUM ('VALIDATION');


CREATE TABLE emails(
    id_emails SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES Users(id_users),
    creation_date TIMESTAMPTZ NOT NULL,
    mail_type mail_types NOT NULL
);