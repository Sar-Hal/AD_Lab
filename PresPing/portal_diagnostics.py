#!/usr/bin/env python3
"""
portal_diagnostics.py
Simple diagnostic tool to analyze HTTP 403 responses and related server info.
Usage:
  python PresPing/portal_diagnostics.py https://presiunivefc.in

Notes:
- Do not use this to bypass authentication or access controls.
- Use only for lawful diagnostics and to help contact your university IT support.
"""
import argparse
import socket
import ssl
import sys
import textwrap
from urllib.parse import urlparse

import requests

DEFAULT_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)


def resolve_host(host):
    try:
        ips = socket.getaddrinfo(host, None)
        addrs = sorted({x[4][0] for x in ips})
        return addrs
    except Exception as e:
        return [f"error: {e}"]


def fetch_cert(host, port=443, timeout=5):
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((host, port), timeout=timeout) as sock:
            with ctx.wrap_socket(sock, server_hostname=host) as ssock:
                cert = ssock.getpeercert()
                return cert
    except Exception as e:
        return {'error': str(e)}


def http_fetch(url, headers=None, timeout=10, allow_redirects=True):
    try:
        s = requests.Session()
        r = s.get(url, headers=headers or {}, timeout=timeout, allow_redirects=allow_redirects)
        return r
    except requests.exceptions.RequestException as e:
        return e


def print_header_block(title):
    print("\n" + (title) + "\n" + ("-" * len(title)))


def analyze_response(resp, url):
    if isinstance(resp, Exception):
        print_header_block("Request Error")
        print(resp)
        return

    print_header_block(f"HTTP {resp.status_code} {resp.reason}")
    print(f"URL: {url}")
    print(f"Final URL: {resp.url}")

    print_header_block("Response Headers")
    for k, v in resp.headers.items():
        print(f"{k}: {v}")

    print_header_block("Security / Server Hints")
    server = resp.headers.get('Server')
    if server:
        print(f"Server header: {server}")
    if 'cloudflare' in (server or '').lower() or resp.headers.get('CF-Ray') or resp.headers.get('cf-ray'):
        print("Cloudflare protection detected (Cloudflare headers present)")
    if 'mod_security' in (resp.text or '').lower() or 'forbidden' in (resp.text or '').lower():
        print("Potential mod_security or web application firewall message in body")

    # Cookie hints
    cookies = resp.cookies
    if cookies:
        print_header_block("Set-Cookie (sample)")
        for k, v in cookies.items():
            print(f"{k}={v}")

    # Body snippet
    print_header_block("Body Snippet")
    body = resp.text or ''
    snippet = body.strip().replace('\n', ' ')[:1000]
    print(textwrap.fill(snippet, width=120))


def main():
    p = argparse.ArgumentParser(description="Diagnose HTTP 403 / access errors for a given URL")
    p.add_argument('url', help='Full URL to check (include https://)')
    p.add_argument('--ua', help='User-Agent string to use', default=DEFAULT_UA)
    p.add_argument('--no-robots', action='store_true', help='Skip robots.txt check')
    p.add_argument('--timeout', type=float, default=10.0, help='Network timeout seconds')
    p.add_argument('--allow-redirects', action='store_true', help='Allow redirects when fetching')
    args = p.parse_args()

    url = args.url
    parsed = urlparse(url)
    if not parsed.scheme:
        print('Please provide a full URL including scheme (https://)')
        sys.exit(1)

    host = parsed.hostname
    port = parsed.port or (443 if parsed.scheme == 'https' else 80)

    print_header_block('Target')
    print(f"URL: {url}")
    print(f"Host: {host}")
    print(f"Scheme: {parsed.scheme}")

    print_header_block('DNS')
    addrs = resolve_host(host)
    for a in addrs:
        print(a)

    if parsed.scheme == 'https':
        print_header_block('TLS Certificate')
        cert = fetch_cert(host, port=port, timeout=args.timeout)
        if isinstance(cert, dict) and cert.get('error'):
            print('Error fetching certificate:', cert['error'])
        else:
            subj = cert.get('subject')
            issuer = cert.get('issuer')
            not_before = cert.get('notBefore')
            not_after = cert.get('notAfter')
            print('Subject:', subj)
            print('Issuer:', issuer)
            print('Not Before:', not_before)
            print('Not After:', not_after)

    headers = {
        'User-Agent': args.ua,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': f"{parsed.scheme}://{host}/",
    }

    print_header_block('Request (with common browser headers)')
    print('User-Agent:', args.ua)

    resp = http_fetch(url, headers=headers, timeout=args.timeout, allow_redirects=args.allow_redirects)
    analyze_response(resp, url)

    if not args.no_robots:
        robots_url = f"{parsed.scheme}://{host}/robots.txt"
        print_header_block('robots.txt')
        r2 = http_fetch(robots_url, headers={'User-Agent': args.ua}, timeout=args.timeout, allow_redirects=True)
        if isinstance(r2, Exception):
            print('robots.txt fetch error:', r2)
        else:
            print('Status:', r2.status_code)
            s = (r2.text or '').strip()
            print(s[:1000] or '(empty)')

    # Suggestions
    print_header_block('Suggestions')
    if isinstance(resp, Exception):
        print('- Network error. Check connectivity and proxy settings.')
    else:
        if resp.status_code == 403:
            print('- 403 Forbidden: resource is accessible but server refused the request.')
            print('- Confirm you are using the correct URL and that the site requires authentication.')
            print('- Try accessing the site in a browser with developer tools open to inspect cookies and requests.')
            print('- If campus-only, connect to the campus/VPN before accessing. Contact your university IT if unsure.')
            if 'cloudflare' in (resp.headers.get('Server') or '').lower() or resp.headers.get('CF-Ray'):
                print('- Cloudflare or similar protection detected: site may require browser JavaScript challenge or cookies.')
            if 'WWW-Authenticate' in resp.headers:
                print('- Server requested authentication (WWW-Authenticate header present). Use proper credentials.')
        elif resp.status_code in (401, 407):
            print('- Authentication required (401/407). Provide credentials or configure proxy auth.')
        elif resp.status_code in (301, 302, 307, 308):
            print('- Redirect detected. Try allowing redirects to follow login flows.')
        else:
            print('- Status is', resp.status_code, '- inspect headers and body snippet above for clues.')

    print('\nDone. Use these findings when contacting your university IT. Do not attempt to bypass access controls.')


if __name__ == '__main__':
    main()
