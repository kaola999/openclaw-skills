#!/usr/bin/env python3
"""
Simplified database CLI for PostgreSQL, MySQL, and SQLite.
"""

import argparse
import os
import sys
import json
import subprocess
import csv
import io
from pathlib import Path
from urllib.parse import urlparse

CONFIG_DIR = Path.home() / ".config" / "db-cli"
PROFILES_FILE = CONFIG_DIR / "profiles.json"

def ensure_config():
    """Ensure config directory exists."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

def load_profiles():
    """Load saved connection profiles."""
    if PROFILES_FILE.exists():
        return json.loads(PROFILES_FILE.read_text())
    return {}

def save_profiles(profiles):
    """Save connection profiles."""
    ensure_config()
    PROFILES_FILE.write_text(json.dumps(profiles, indent=2))

def get_profile(name):
    """Get a saved profile."""
    profiles = load_profiles()
    return profiles.get(name)

def run_postgres(args):
    """Run PostgreSQL commands."""
    # Build connection parameters
    host = args.host or "localhost"
    port = args.port or 5432
    database = args.db or args.database or "postgres"
    user = args.user or os.getenv("PGUSER") or "postgres"
    password = args.password or os.getenv("PGPASSWORD")
    
    env = os.environ.copy()
    if password:
        env["PGPASSWORD"] = password
    
    if args.exec:
        # Run single query
        cmd = [
            "psql",
            "-h", host,
            "-p", str(port),
            "-U", user,
            "-d", database,
            "-c", args.exec,
            "--pset", "pager=off"
        ]
        if args.csv:
            cmd.extend(["--csv"])
        subprocess.run(cmd, env=env)
    elif args.list_tables:
        cmd = [
            "psql",
            "-h", host,
            "-p", str(port),
            "-U", user,
            "-d", database,
            "-c", "\\dt",
            "--pset", "pager=off"
        ]
        subprocess.run(cmd, env=env)
    elif args.schema:
        cmd = [
            "psql",
            "-h", host,
            "-p", str(port),
            "-U", user,
            "-d", database,
            "-c", f"\\d {args.schema}",
            "--pset", "pager=off"
        ]
        subprocess.run(cmd, env=env)
    elif args.table and args.csv:
        cmd = [
            "psql",
            "-h", host,
            "-p", str(port),
            "-U", user,
            "-d", database,
            "-c", f"SELECT * FROM {args.table}",
            "--csv"
        ]
        subprocess.run(cmd, env=env)
    else:
        # Interactive shell
        cmd = [
            "psql",
            "-h", host,
            "-p", str(port),
            "-U", user,
            "-d", database
        ]
        subprocess.run(cmd, env=env)

def run_mysql(args):
    """Run MySQL commands."""
    host = args.host or "localhost"
    port = args.port or 3306
    database = args.db or args.database
    user = args.user or os.getenv("MYSQL_USER") or "root"
    password = args.password or os.getenv("MYSQL_PASSWORD") or os.getenv("MYSQL_PWD")
    
    if args.exec:
        cmd = [
            "mysql",
            "-h", host,
            "-P", str(port),
            "-u", user,
        ]
        if password:
            cmd.extend([f"-p{password}"])
        if database:
            cmd.extend(["-D", database])
        cmd.extend(["-e", args.exec])
        subprocess.run(cmd)
    elif args.table and args.csv:
        cmd = [
            "mysql",
            "-h", host,
            "-P", str(port),
            "-u", user,
        ]
        if password:
            cmd.extend([f"-p{password}"])
        if database:
            cmd.extend(["-D", database])
        cmd.extend([
            "-e", f"SELECT * FROM {args.table}",
            "--batch",
            "--raw"
        ])
        result = subprocess.run(cmd, capture_output=True, text=True)
        # Convert tab-separated to CSV
        lines = result.stdout.strip().split('\n')
        if lines:
            writer = csv.writer(sys.stdout)
            for line in lines:
                writer.writerow(line.split('\t'))
    else:
        # Interactive shell
        cmd = [
            "mysql",
            "-h", host,
            "-P", str(port),
            "-u", user,
        ]
        if password:
            cmd.extend([f"-p{password}"])
        if database:
            cmd.extend(["-D", database])
        subprocess.run(cmd)

def run_sqlite(args):
    """Run SQLite commands."""
    db_file = args.file or args.database
    
    if not db_file:
        print("Error: SQLite requires --file or -f argument")
        sys.exit(1)
    
    if args.exec:
        cmd = ["sqlite3", db_file, args.exec]
        if args.csv and args.exec.upper().startswith("SELECT"):
            # Add CSV headers
            cmd = ["sqlite3", "-header", "-csv", db_file, args.exec]
        subprocess.run(cmd)
    elif args.table and args.csv:
        cmd = ["sqlite3", "-header", "-csv", db_file, f"SELECT * FROM {args.table}"]
        subprocess.run(cmd)
    else:
        # Interactive shell
        cmd = ["sqlite3", db_file]
        subprocess.run(cmd)

def profile_add(args):
    """Add a new connection profile."""
    profiles = load_profiles()
    profiles[args.name] = {
        "type": args.type,
        "host": args.host,
        "port": args.port,
        "database": args.db,
        "user": args.user
    }
    save_profiles(profiles)
    print(f"Profile '{args.name}' saved.")

def profile_list(args):
    """List saved profiles."""
    profiles = load_profiles()
    if not profiles:
        print("No saved profiles.")
        return
    
    print("\nSaved Profiles:\n")
    for name, config in profiles.items():
        print(f"  {name}")
        print(f"    Type: {config['type']}")
        print(f"    Host: {config.get('host', 'N/A')}")
        print(f"    Database: {config.get('database', 'N/A')}")
        print()

def main():
    parser = argparse.ArgumentParser(description="Simplified database CLI")
    subparsers = parser.add_subparsers(dest="command", help="Database type")
    
    # PostgreSQL
    pg_parser = subparsers.add_parser("pg", help="PostgreSQL operations")
    pg_parser.add_argument("--host", "-h", help="Database host")
    pg_parser.add_argument("--port", "-p", type=int, help="Database port")
    pg_parser.add_argument("--db", "--database", "-d", help="Database name")
    pg_parser.add_argument("--user", "-u", help="Database user")
    pg_parser.add_argument("--password", help="Database password")
    pg_parser.add_argument("--exec", "-e", help="Execute SQL query")
    pg_parser.add_argument("--list-tables", "-l", action="store_true", help="List all tables")
    pg_parser.add_argument("--schema", "-s", help="Show table schema")
    pg_parser.add_argument("--table", "-t", help="Table name for export")
    pg_parser.add_argument("--csv", "-c", action="store_true", help="Output as CSV")
    pg_parser.add_argument("--profile", help="Use saved profile")
    
    # MySQL
    mysql_parser = subparsers.add_parser("mysql", help="MySQL operations")
    mysql_parser.add_argument("--host", "-h", help="Database host")
    mysql_parser.add_argument("--port", "-p", type=int, help="Database port")
    mysql_parser.add_argument("--db", "--database", "-d", help="Database name")
    mysql_parser.add_argument("--user", "-u", help="Database user")
    mysql_parser.add_argument("--password", help="Database password")
    mysql_parser.add_argument("--exec", "-e", help="Execute SQL query")
    mysql_parser.add_argument("--table", "-t", help="Table name for export")
    mysql_parser.add_argument("--csv", "-c", action="store_true", help="Output as CSV")
    mysql_parser.add_argument("--profile", help="Use saved profile")
    
    # SQLite
    sqlite_parser = subparsers.add_parser("sqlite", help="SQLite operations")
    sqlite_parser.add_argument("--file", "-f", help="Database file path")
    sqlite_parser.add_argument("--database", "-d", help="Database file path (alias)")
    sqlite_parser.add_argument("--exec", "-e", help="Execute SQL query")
    sqlite_parser.add_argument("--table", "-t", help="Table name for export")
    sqlite_parser.add_argument("--csv", "-c", action="store_true", help="Output as CSV")
    
    # Profile management
    profile_parser = subparsers.add_parser("profile", help="Manage connection profiles")
    profile_subparsers = profile_parser.add_subparsers(dest="profile_cmd")
    
    profile_add_parser = profile_subparsers.add_parser("add", help="Add a profile")
    profile_add_parser.add_argument("name", help="Profile name")
    profile_add_parser.add_argument("--type", required=True, choices=["pg", "mysql", "sqlite"])
    profile_add_parser.add_argument("--host", help="Database host")
    profile_add_parser.add_argument("--port", type=int, help="Database port")
    profile_add_parser.add_argument("--db", "--database", help="Database name")
    profile_add_parser.add_argument("--user", help="Database user")
    
    profile_list_parser = profile_subparsers.add_parser("list", help="List profiles")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Load profile if specified
    if hasattr(args, 'profile') and args.profile:
        profile = get_profile(args.profile)
        if not profile:
            print(f"Profile '{args.profile}' not found.")
            sys.exit(1)
        args.host = args.host or profile.get('host')
        args.port = args.port or profile.get('port')
        args.db = args.db or profile.get('database')
        args.user = args.user or profile.get('user')
    
    if args.command == "pg":
        run_postgres(args)
    elif args.command == "mysql":
        run_mysql(args)
    elif args.command == "sqlite":
        run_sqlite(args)
    elif args.command == "profile":
        if args.profile_cmd == "add":
            profile_add(args)
        elif args.profile_cmd == "list":
            profile_list(args)
        else:
            profile_parser.print_help()

if __name__ == "__main__":
    main()
