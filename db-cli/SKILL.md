---
name: db-cli
description: Quick database operations for PostgreSQL, MySQL, and SQLite. Use when connecting to databases, running queries, exporting data, or managing database connections without remembering complex CLI syntax.
---

# Database CLI (db-cli)

Simplified database operations for common tasks.

## Quick Start

Connect to a database:
```bash
# PostgreSQL
db pg --host localhost --db myapp --user postgres

# MySQL
db mysql --host localhost --db myapp --user root

# SQLite (file-based)
db sqlite --file ~/data/app.db
```

Run a query:
```bash
db pg --db myapp --exec "SELECT * FROM users LIMIT 10"
```

Export to CSV:
```bash
db pg --db myapp --query "SELECT * FROM orders" --csv > orders.csv
```

## Commands

### PostgreSQL

```bash
# Interactive shell
db pg --host <host> --port 5432 --db <database> --user <user>

# Run single query
db pg --db myapp --exec "SELECT COUNT(*) FROM users"

# Export table to CSV
db pg --db myapp --table users --csv

# List tables
db pg --db myapp --list-tables

# Show table schema
db pg --db myapp --schema users
```

### MySQL

```bash
# Interactive shell
db mysql --host <host> --port 3306 --db <database> --user <user>

# Run query
db mysql --db myapp --exec "SHOW TABLES"

# Export to CSV
db mysql --db myapp --table orders --csv
```

### SQLite

```bash
# Interactive shell
db sqlite --file ~/data/app.db

# Run query
db sqlite --file app.db --exec ".tables"

# Export table
db sqlite --file app.db --table users --csv
```

## Connection Profiles

Save frequently used connections:

```bash
# Save a profile
db profile add prod-pg --type pg --host prod.db.com --db production --user admin

# Use saved profile
db pg --profile prod-pg --exec "SELECT * FROM logs"

# List profiles
db profile list
```

## Resources

### scripts/

- `db.py` - Main CLI script for database operations
