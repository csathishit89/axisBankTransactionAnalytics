CREATE TABLE account (
    account_id serial PRIMARY KEY,
	account_number VARCHAR(20),
    account_name VARCHAR(100),
    account_type VARCHAR(50),
    ifsc_code VARCHAR(11),
	branch VARCHAR(100),
	customer_id VARCHAR(20),
	currency VARCHAR(3),
	statement_from_date DATE,
	statement_to_date DATE,
	opening_balance DECIMAL(15,2),
	total_credits DECIMAL(15,2),
	total_debits DECIMAL(15,2),
	closing_balance DECIMAL(15,2),
	total_transactions DECIMAL(15,2),
	created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE transaction (
    transaction_id serial PRIMARY KEY,
	account_id BIGINT,
    transaction_date DATE,
    description_text VARCHAR(100),
    reference VARCHAR(50),
	transaction_type VARCHAR(2)
        CHECK (transaction_type IN ('DR', 'CR')),
	debit_amount DECIMAL(15,2),
	credit_amount DECIMAL(15,2),
	balance DECIMAL(15,2),
	raw_narration TEXT,
	created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE category (
    category_id serial PRIMARY KEY,
	transaction_id BIGINT,
    category VARCHAR(50),
    sub_category VARCHAR(50),
    confidence DECIMAL(5,4),
	rule_applied VARCHAR(80),
	assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE users (
    user_id serial PRIMARY KEY,
	userid VARCHAR(20),
    user_password VARCHAR(50),
    user_role VARCHAR(20)
        CHECK (user_role IN ('Customer', 'Management', 'BranchManager')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);