#!/usr/bin/env python3
"""
Simple API testing and HTTP client.
"""

import argparse
import json
import sys
import urllib.request
import urllib.parse
import urllib.error
from pathlib import Path
from base64 import b64encode

CONFIG_DIR = Path.home() / ".config" / "api-tester"
REQUESTS_FILE = CONFIG_DIR / "requests.json"

def ensure_config():
    """Ensure config directory exists."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

def load_requests():
    """Load saved requests."""
    if REQUESTS_FILE.exists():
        return json.loads(REQUESTS_FILE.read_text())
    return {}

def save_requests(requests):
    """Save requests."""
    ensure_config()
    REQUESTS_FILE.write_text(json.dumps(requests, indent=2))

def make_request(method, url, headers=None, data=None, timeout=30, follow_redirects=True):
    """Make HTTP request."""
    req = urllib.request.Request(url, method=method)
    
    # Add headers
    if headers:
        for key, value in headers.items():
            req.add_header(key, value)
    
    # Add data
    if data:
        if isinstance(data, dict):
            data = json.dumps(data).encode('utf-8')
            req.add_header('Content-Type', 'application/json')
        elif isinstance(data, str):
            data = data.encode('utf-8')
        req.data = data
    
    try:
        response = urllib.request.urlopen(req, timeout=timeout)
        return {
            'status': response.status,
            'headers': dict(response.headers),
            'body': response.read().decode('utf-8')
        }
    except urllib.error.HTTPError as e:
        return {
            'status': e.code,
            'headers': dict(e.headers),
            'body': e.read().decode('utf-8'),
            'error': True
        }
    except Exception as e:
        return {
            'error': True,
            'message': str(e)
        }

def format_response(response, args):
    """Format and print response."""
    if args.status_only:
        print(response['status'])
        return
    
    if args.headers_only:
        for key, value in response.get('headers', {}).items():
            print(f"{key}: {value}")
        return
    
    if args.include:
        print(f"HTTP {response['status']}")
        for key, value in response.get('headers', {}).items():
            print(f"{key}: {value}")
        print()
    
    body = response.get('body', '')
    
    # Try to parse as JSON
    try:
        json_body = json.loads(body)
        if args.jq:
            # Simple jq-like filtering (just key access)
            keys = args.jq.replace('.', '').split(',')
            result = {}
            for key in keys:
                key = key.strip()
                if key in json_body:
                    result[key] = json_body[key]
            if len(result) == 1:
                print(json.dumps(list(result.values())[0], indent=2 if args.pretty else None))
            else:
                print(json.dumps(result, indent=2 if args.pretty else None))
        elif args.field:
            if args.field in json_body:
                value = json_body[args.field]
                if isinstance(value, (dict, list)):
                    print(json.dumps(value, indent=2 if args.pretty else None))
                else:
                    print(value)
        elif args.pretty:
            print(json.dumps(json_body, indent=2))
        else:
            print(body)
    except json.JSONDecodeError:
        print(body)

def cmd_request(method, args):
    """Execute HTTP request."""
    # Build URL with query params
    url = args.url
    if args.param:
        params = urllib.parse.urlencode(args.param)
        url = f"{url}?{params}"
    
    # Build headers
    headers = {}
    if args.header:
        for h in args.header:
            if ':' in h:
                key, value = h.split(':', 1)
                headers[key.strip()] = value.strip()
    
    # Build data
    data = None
    if args.json:
        data = args.json
        headers['Content-Type'] = 'application/json'
    elif args.form:
        data = args.form
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
    elif args.file:
        # Simple file upload (read file content)
        if '=' in args.file:
            field_name, file_path = args.file.split('=', 1)
            if file_path.startswith('@'):
                file_path = file_path[1:]
            try:
                with open(file_path, 'rb') as f:
                    data = f.read()
                headers['Content-Type'] = 'application/octet-stream'
            except FileNotFoundError:
                print(f"File not found: {file_path}")
                sys.exit(1)
    
    # Make request
    response = make_request(
        method=method,
        url=url,
        headers=headers,
        data=data,
        timeout=args.timeout or 30,
        follow_redirects=args.follow
    )
    
    if 'error' in response and 'message' in response:
        print(f"Error: {response['message']}")
        sys.exit(1)
    
    # Save response if requested
    if args.save:
        Path(args.save).write_text(response.get('body', ''))
        print(f"Response saved to {args.save}")
    
    # Format and print
    format_response(response, args)

def cmd_save(args):
    """Save a request."""
    requests = load_requests()
    requests[args.name] = {
        'method': args.method.upper(),
        'url': args.url,
        'headers': args.header or [],
        'json': args.json,
        'form': args.form
    }
    save_requests(requests)
    print(f"Request '{args.name}' saved.")

def cmd_run(args):
    """Run a saved request."""
    requests = load_requests()
    if args.name not in requests:
        print(f"Request '{args.name}' not found.")
        sys.exit(1)
    
    req = requests[args.name]
    
    # Create args object
    class Args:
        pass
    
    run_args = Args()
    run_args.url = req['url']
    run_args.header = req.get('headers', [])
    run_args.param = []
    run_args.json = req.get('json')
    run_args.form = req.get('form')
    run_args.file = None
    run_args.timeout = 30
    run_args.follow = False
    run_args.headers_only = False
    run_args.include = False
    run_args.save = None
    run_args.pretty = True
    run_args.jq = None
    run_args.field = None
    run_args.status_only = False
    
    cmd_request(req['method'], run_args)

def cmd_list(args):
    """List saved requests."""
    requests = load_requests()
    if not requests:
        print("No saved requests.")
        return
    
    print("\nSaved Requests:\n")
    for name, req in requests.items():
        print(f"  {name}")
        print(f"    {req['method']} {req['url']}")
        print()

def cmd_delete(args):
    """Delete a saved request."""
    requests = load_requests()
    if args.name not in requests:
        print(f"Request '{args.name}' not found.")
        sys.exit(1)
    
    del requests[args.name]
    save_requests(requests)
    print(f"Request '{args.name}' deleted.")

def main():
    parser = argparse.ArgumentParser(description="Simple API tester")
    subparsers = parser.add_subparsers(dest="command", help="Command")
    
    # HTTP methods
    for method in ['get', 'post', 'put', 'patch', 'delete', 'head']:
        method_parser = subparsers.add_parser(method, help=f"{method.upper()} request")
        method_parser.add_argument("url", help="Request URL")
        method_parser.add_argument("--header", "-H", action="append", help="Request header")
        method_parser.add_argument("--param", "-p", action="append", help="Query parameter (key=value)")
        method_parser.add_argument("--json", "-j", help="JSON body")
        method_parser.add_argument("--form", "-f", help="Form data")
        method_parser.add_argument("--file", help="File upload (field=@path)")
        method_parser.add_argument("--timeout", "-t", type=int, help="Request timeout")
        method_parser.add_argument("--follow", "-L", action="store_true", help="Follow redirects")
        method_parser.add_argument("--headers-only", action="store_true", help="Show headers only")
        method_parser.add_argument("--include", "-i", action="store_true", help="Include response headers")
        method_parser.add_argument("--save", "-o", help="Save response to file")
        method_parser.add_argument("--pretty", action="store_true", help="Pretty print JSON")
        method_parser.add_argument("--jq", help="Filter JSON (simple key access)")
        method_parser.add_argument("--field", help="Extract specific field")
        method_parser.add_argument("--status-only", "-s", action="store_true", help="Show status code only")
    
    # save
    save_parser = subparsers.add_parser("save", help="Save a request")
    save_parser.add_argument("name", help="Request name")
    save_parser.add_argument("--method", "-m", required=True, help="HTTP method")
    save_parser.add_argument("--url", "-u", required=True, help="Request URL")
    save_parser.add_argument("--header", "-H", action="append", help="Request header")
    save_parser.add_argument("--json", "-j", help="JSON body")
    save_parser.add_argument("--form", "-f", help="Form data")
    
    # run
    run_parser = subparsers.add_parser("run", help="Run saved request")
    run_parser.add_argument("name", help="Request name")
    
    # list
    list_parser = subparsers.add_parser("list", help="List saved requests")
    
    # delete
    delete_parser = subparsers.add_parser("delete", help="Delete saved request")
    delete_parser.add_argument("name", help="Request name")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Parse params
    if hasattr(args, 'param') and args.param:
        parsed_params = []
        for p in args.param:
            if '=' in p:
                parsed_params.append(p)
        args.param = parsed_params
    
    if args.command in ['get', 'post', 'put', 'patch', 'delete', 'head']:
        cmd_request(args.command.upper(), args)
    elif args.command == "save":
        cmd_save(args)
    elif args.command == "run":
        cmd_run(args)
    elif args.command == "list":
        cmd_list(args)
    elif args.command == "delete":
        cmd_delete(args)

if __name__ == "__main__":
    main()
