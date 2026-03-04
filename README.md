# OpenClaw Skills

Useful OpenClaw agent skills for database operations, Docker management, and API testing.

## Skills

### db-cli
Simplified database operations for PostgreSQL, MySQL, and SQLite.

```bash
# Quick connect
db pg --host localhost --db myapp --user postgres

# Run query
db pg --db myapp --exec "SELECT * FROM users LIMIT 10"

# Export to CSV
db pg --db myapp --table users --csv
```

[View db-cli docs](db-cli/SKILL.md)

### docker-ctl
Simplified Docker and Docker Compose operations.

```bash
# List containers
docker-ctl ps

# Quick run
docker-ctl run nginx --port 8080:80

# Compose stack
docker-ctl compose up -d
```

[View docker-ctl docs](docker-ctl/SKILL.md)

### api-tester
Simple HTTP client for API testing and debugging.

```bash
# GET request
api get https://api.example.com/users

# POST JSON
api post https://api.example.com/users --json '{"name": "John"}'

# With headers
api get https://api.example.com/users --header "Authorization: Bearer token"
```

[View api-tester docs](api-tester/SKILL.md)

## Installation

### Via ClawHub

```bash
clawhub install db-cli
clawhub install docker-ctl
clawhub install api-tester
```

### Manual Installation

1. Download the `.skill` file from [Releases](../../releases)
2. Extract to your OpenClaw skills directory:
   ```bash
   unzip db-cli.skill -d ~/.openclaw/workspace/skills/
   ```

## Development

These skills are built using the [skill-creator](https://github.com/openclaw/openclaw/tree/main/extensions/skill-creator) workflow.

To package a skill:
```bash
python3 scripts/package_skill.py <skill-folder>
```

## License

MIT

## Support

If you find these skills useful, consider supporting the development:

[![Buy Me a Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-ffdd00?style=flat&logo=buy-me-a-coffee&logoColor=black)]()

## Contributing

Pull requests are welcome! Please feel free to submit issues or feature requests.
