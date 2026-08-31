#!/usr/bin/env python3
"""
AccFo Self-Hostable Sync Server
Ultra-lightweight, zero-dependency Python server for cross-device encrypted vault synchronization.
Data is 100% End-to-End Encrypted (E2EE) on the client before reaching this server.

Security Hardened:
- Constant-time HMAC comparison (hmac.compare_digest) to eliminate timing attacks
- 10MB payload size limits to protect against memory exhaustion (DoS)
- Sanitized file paths (safe data directory containment)
- Sanitized JSON responses

Usage:
    python sync_server/server.py [PORT] [AUTH_TOKEN]

Example:
    python sync_server/server.py 8765 my_secret_token_123
"""

import sys
import os
import json
import hmac
from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
AUTH_TOKEN = (
    sys.argv[2]
    if len(sys.argv) > 2
    else os.environ.get("ACCFO_SYNC_TOKEN", "accfo_secret_token")
)
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vault_data")
VAULT_FILE = os.path.join(DATA_DIR, "vault.json")
MAX_PAYLOAD_BYTES = 10 * 1024 * 1024  # 10 MB

os.makedirs(DATA_DIR, exist_ok=True)


class SyncHandler(BaseHTTPRequestHandler):
    def _send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("X-Content-Type-Options", "nosniff")

    def do_OPTIONS(self):
        self.send_response(204)
        self._send_cors_headers()
        self.end_headers()

    def _verify_auth(self):
        if not AUTH_TOKEN:
            return True
        auth_header = self.headers.get("Authorization", "")
        expected = f"Bearer {AUTH_TOKEN}"
        # Constant-time comparison to prevent timing attacks
        return hmac.compare_digest(
            auth_header.encode("utf-8"), expected.encode("utf-8")
        )

    def do_GET(self):
        if self.path != "/api/vault" and not self.path.startswith("/api/vault"):
            self.send_response(404)
            self._send_cors_headers()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"error": "Not Found"}')
            return

        if not self._verify_auth():
            self.send_response(401)
            self._send_cors_headers()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"error": "Unauthorized"}')
            return

        if not os.path.exists(VAULT_FILE):
            self.send_response(404)
            self._send_cors_headers()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"error": "Vault not found"}')
            return

        try:
            with open(VAULT_FILE, "r", encoding="utf-8") as f:
                content = f.read()
            self.send_response(200)
            self._send_cors_headers()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(content.encode("utf-8"))
        except Exception as e:
            self.send_response(500)
            self._send_cors_headers()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(
                json.dumps({"error": "Internal Server Error"}).encode("utf-8")
            )

    def do_POST(self):
        if self.path != "/api/vault" and not self.path.startswith("/api/vault"):
            self.send_response(404)
            self._send_cors_headers()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"error": "Not Found"}')
            return

        if not self._verify_auth():
            self.send_response(401)
            self._send_cors_headers()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"error": "Unauthorized"}')
            return

        try:
            content_length = int(self.headers.get("Content-Length", 0))
        except ValueError:
            content_length = 0

        if content_length <= 0 or content_length > MAX_PAYLOAD_BYTES:
            self.send_response(413)  # Payload Too Large
            self._send_cors_headers()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(
                b'{"error": "Payload exceeds 10MB limit or invalid length"}'
            )
            return

        body = self.rfile.read(content_length)

        try:
            # Validate that body is parseable JSON before saving
            json.loads(body.decode("utf-8"))
            with open(VAULT_FILE, "w", encoding="utf-8") as f:
                f.write(body.decode("utf-8"))
            self.send_response(200)
            self._send_cors_headers()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(
                b'{"status": "ok", "message": "Vault synchronized successfully"}'
            )
        except json.JSONDecodeError:
            self.send_response(400)
            self._send_cors_headers()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"error": "Malformed JSON payload"}')
        except Exception:
            self.send_response(500)
            self._send_cors_headers()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"error": "Internal Server Error"}')

    def log_message(self, format, *args):
        # Custom clean log format
        sys.stderr.write(f"[AccFo Sync] {self.address_string()} - {format % args}\n")


if __name__ == "__main__":
    # Ensure UTF-8 output on Windows console
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
    print(f"[AccFo Sync] Server starting on port {PORT}")
    print(f"[AccFo Sync] Auth Token: {AUTH_TOKEN}")
    print(
        f"[AccFo Sync] Connect URL in AccFo Settings: http://localhost:{PORT}/api/vault"
    )
    server = HTTPServer(("0.0.0.0", PORT), SyncHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[AccFo Sync] Stopping server...")
        server.server_close()
