#!/usr/bin/env python3
"""Simple mock Bankr server for local testing.

Endpoints:
- POST /agent/prompt -> returns {"jobId": "job123"}
- GET  /agent/job/job123 -> returns {"status": "completed", "transactions": [], "result": {"price": "1.23"}}
"""
from http.server import BaseHTTPRequestHandler, HTTPServer
import json

class Handler(BaseHTTPRequestHandler):
    def _send(self, code, obj):
        b = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_POST(self):
        if self.path == '/agent/prompt':
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length) if length else b''
            try:
                req = json.loads(body.decode() or '{}')
            except Exception:
                req = {}
            # Echo back a jobId
            return self._send(200, {'jobId': 'job123'})
        self._send(404, {'error': 'not_found'})

    def do_GET(self):
        if self.path.startswith('/agent/job/'):
            # Return a response that can vary based on the original prompt
            # For simplicity we look for a last_prompt.txt file written by tests
            try:
                with open('last_prompt.txt', 'r') as f:
                    prompt = f.read().lower()
            except Exception:
                prompt = ''

            # If prompt asks for a 'delay' test, simulate a stuck/pending job
            if 'delay' in prompt or 'pending' in prompt:
                return self._send(200, {
                    'status': 'pending',
                    'transactions': [],
                })

            if 'solana' in prompt or 'sol' in prompt:
                return self._send(200, {
                    'status': 'completed',
                    'transactions': [],
                    'result': {'price': '20.00', 'chain': 'solana', 'note': 'devnet-mock'},
                })

            return self._send(200, {
                'status': 'completed',
                'transactions': [],
                'result': {'price': '1.23', 'note': 'mocked'},
            })
        self._send(404, {'error': 'not_found'})

if __name__ == '__main__':
    server = HTTPServer(('127.0.0.1', 8000), Handler)
    print('Mock Bankr server listening on http://127.0.0.1:8000')
    server.serve_forever()
