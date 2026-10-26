"""Minimal JSON API and static file server for the explorer.

Only the standard library is used: ThreadingHTTPServer plus a small router.
The server binds to localhost because the workshop runs on the student's
machine; nothing here is meant for public deployment.
"""

import json
import mimetypes
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

from .narino_taxonomy import Explorer

MAX_BODY = 1_000_000


def _param(query, name, default=None):
    values = query.get(name)
    if not values:
        if default is not None:
            return default
        raise ValueError(f"Missing query parameter '{name}'")
    return values[0]


def _int_param(query, name, default=None):
    raw = _param(query, name, default)
    if raw is None:
        raise ValueError(f"Missing query parameter '{name}'")
    try:
        return int(raw)
    except (TypeError, ValueError):
        raise ValueError(f"Query parameter '{name}' must be an integer, got '{raw}'")


def _int_field(data, name):
    if name not in data:
        raise ValueError(f"Missing field '{name}'")
    value = data[name]
    if isinstance(value, bool):
        raise ValueError(f"Field '{name}' must be a whole number")
    try:
        return int(value)
    except (TypeError, ValueError):
        raise ValueError(f"Field '{name}' must be a whole number, got '{value}'")


def build_handler(explorer, web_dir, lock):
    web_root = Path(web_dir).resolve()

    class Handler(BaseHTTPRequestHandler):
        server_version = "NarinoTaxonomy/1.0"

        def do_GET(self):
            try:
                with lock:
                    self._route_get()
            except KeyError as exc:
                self._error(404, exc.args[0] if exc.args else "Not found")
            except FileNotFoundError:
                self._error(404, "The requested file does not exist")
            except ValueError as exc:
                self._error(400, str(exc))
            except Exception as exc:
                self._error(500, f"Unexpected server error: {exc}")

        def do_POST(self):
            try:
                with lock:
                    self._route_post()
            except KeyError as exc:
                self._error(404, exc.args[0] if exc.args else "Not found")
            except ValueError as exc:
                self._error(400, str(exc))
            except Exception as exc:
                self._error(500, f"Unexpected server error: {exc}")

        def _route_get(self):
            parsed = urlparse(self.path)
            query = parse_qs(parsed.query)
            path = parsed.path
            if path == "/api/tree":
                self._json(explorer.tree_view())
            elif path == "/api/node":
                self._json(explorer.navigate(_param(query, "key")))
            elif path == "/api/lca":
                self._json(explorer.common_ancestor(_param(query, "a"), _param(query, "b")))
            elif path == "/api/traversal":
                self._json(explorer.traverse(_param(query, "type", "preorder")))
            elif path == "/api/range":
                self._json(explorer.by_altitude(_int_param(query, "lo"), _int_param(query, "hi")))
            elif path == "/api/autocomplete":
                self._json(
                    explorer.autocomplete(
                        _param(query, "prefix", ""),
                        _int_param(query, "limit", "8"),
                    )
                )
            elif path == "/api/altitude":
                self._json(explorer.altitude_bands())
            elif path == "/api/stats":
                self._json(explorer.stats())
            elif path == "/api/species":
                self._json(
                    {
                        "species": explorer.species_options(),
                        "families": explorer.families(),
                    }
                )
            elif path == "/api/health":
                self._json({"ok": True})
            elif path.startswith("/api/"):
                self._error(404, f"Unknown API route '{path}'")
            else:
                self._static(path)

        def _route_post(self):
            parsed = urlparse(self.path)
            if parsed.path == "/api/species":
                data = self._read_json()
                parent_key = data.get("parent_key", "")
                if not parent_key:
                    raise ValueError("Missing field 'parent_key'")
                created = explorer.add_species(
                    parent_key,
                    data.get("scientific_name", ""),
                    data.get("common_name", ""),
                    _int_field(data, "min_altitude"),
                    _int_field(data, "max_altitude"),
                    data.get("note", ""),
                )
                self._json({"created": created}, 201)
            elif parsed.path == "/api/remove":
                data = self._read_json()
                key = data.get("key", "")
                if not key:
                    raise ValueError("Missing field 'key'")
                self._json({"removed": explorer.remove_branch(key)})
            else:
                self._error(404, f"Unknown API route '{parsed.path}'")

        def _read_json(self):
            raw_length = self.headers.get("Content-Length", "0")
            try:
                length = int(raw_length)
            except ValueError:
                raise ValueError("Invalid Content-Length header")
            if length <= 0:
                raise ValueError("The request body is empty")
            if length > MAX_BODY:
                raise ValueError("The request body is too large")
            raw = self.rfile.read(length)
            try:
                data = json.loads(raw.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                raise ValueError("The request body is not valid JSON")
            if not isinstance(data, dict):
                raise ValueError("The request body must be a JSON object")
            return data

        def _static(self, path):
            if path in ("", "/"):
                path = "/index.html"
            target = (web_root / unquote(path).lstrip("/")).resolve()
            if not target.is_relative_to(web_root):
                self._error(403, "The requested path is outside the web folder")
                return
            if not target.is_file():
                self._error(404, "The requested file does not exist")
                return
            content_type = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
            self._send(200, target.read_bytes(), content_type, cache="no-cache")

        def _json(self, payload, status=200):
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self._send(status, body, "application/json; charset=utf-8", cache="no-store")

        def _error(self, status, message):
            self._json({"error": message}, status)

        def _send(self, status, body, content_type, cache="no-store"):
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", cache)
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header(
                "Content-Security-Policy",
                "default-src 'self'; style-src 'self' 'unsafe-inline'; "
                "script-src 'self' 'unsafe-inline'; img-src 'self' data:;",
            )
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, fmt, *args):
            sys.stderr.write(f"[{self.address_string()}] {fmt % args}\n")

    return Handler


def make_server(port, explorer=None, web_dir=None):
    explorer = explorer or Explorer.with_seed_data()
    if web_dir is None:
        web_dir = Path(__file__).resolve().parents[1] / "web"
    lock = threading.RLock()
    handler = build_handler(explorer, web_dir, lock)
    server = ThreadingHTTPServer(("127.0.0.1", port), handler)
    server.daemon_threads = True
    server.explorer = explorer
    return server
