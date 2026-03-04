---
name: api-tester
description: Simple API testing and HTTP requests. Use when testing REST APIs, making HTTP requests, or debugging endpoints without writing curl commands. Supports JSON, form data, file uploads, and response formatting.
---

# API Tester

Simple HTTP client for API testing and debugging.

## Quick Start

```bash
# GET request
api get https://api.example.com/users

# POST JSON
api post https://api.example.com/users --json '{"name": "John"}'

# With headers
api get https://api.example.com/users --header "Authorization: Bearer token"

# Save response
api get https://api.example.com/users --save response.json
```

## Commands

### HTTP Methods

```bash
# GET
api get <url>

# POST
api post <url> --json '{"key": "value"}'
api post <url> --form 'name=John&age=30'
api post <url> --file upload=@document.pdf

# PUT
api put <url> --json '{"key": "value"}'

# PATCH
api patch <url> --json '{"key": "value"}'

# DELETE
api delete <url>

# HEAD
api head <url>
```

### Options

```bash
# Headers
api get <url> --header "Authorization: Bearer token" --header "X-API-Key: secret"

# Query parameters
api get <url> --param page=1 --param limit=10

# JSON body (auto sets Content-Type)
api post <url> --json '{"name": "test"}'

# Form data
api post <url> --form 'name=John&email=john@example.com'

# File upload
api post <url> --file 'image=@photo.jpg'

# Timeout
api get <url> --timeout 30

# Follow redirects
api get <url> --follow

# Show headers only
api get <url> --headers-only

# Include response headers
api get <url> --include

# Save to file
api get <url> --save output.json

# Pretty print JSON
api get <url> --pretty
```

### Response Formatting

```bash
# Filter JSON with jq syntax
api get https://api.github.com/users/octocat --jq '.login, .id'

# Extract specific field
api get <url> --field name

# Show status code only
api get <url> --status-only
```

### Request Collections

Save and reuse requests:

```bash
# Save request
api save get-users --method get --url https://api.example.com/users --header "Authorization: Bearer token"

# Run saved request
api run get-users

# List saved requests
api list

# Delete saved request
api delete get-users
```

## Examples

```bash
# Test local API
api get http://localhost:3000/health

# GitHub API
api get https://api.github.com/user --header "Authorization: token YOUR_TOKEN"

# POST with JSON
api post https://httpbin.org/post --json '{"test": "data"}' --pretty

# Upload file
api post https://httpbin.org/post --file 'file=@report.pdf' --form 'description=Monthly report'

# Chain with jq
api get https://api.github.com/repos/python/cpython | jq '.stargazers_count'
```

## Resources

### scripts/

- `api.py` - Main CLI script for HTTP requests
