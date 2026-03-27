"""
TaskFlow - Python Backend Server
Run: python server.py
Then open: http://localhost:8000
No external libraries needed!
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json, os, urllib.parse
from datetime import datetime

DATA_FILE = "tasks.json"

# ─── Task Storage ──────────────────────────────────────────────────────────────

def load_tasks():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_tasks(tasks):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=2, ensure_ascii=False)

def next_id(tasks):
    return max((t["id"] for t in tasks), default=0) + 1

# ─── HTTP Handler ──────────────────────────────────────────────────────────────

class Handler(BaseHTTPRequestHandler):

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,PUT,DELETE,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()

    def _static(self, path, ctype):
        if not os.path.exists(path):
            self._json(404, {"error": f"{path} not found"})
            return
        with open(path, "rb") as f:
            data = f.read()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self._cors()
        self.end_headers()
        self.wfile.write(data)

    def _json(self, code, obj):
        body = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self._cors()
        self.end_headers()
        self.wfile.write(body)

    def _body(self):
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length)
        try:
            return json.loads(raw)
        except Exception:
            return {}

    def do_GET(self):
        p = urllib.parse.urlparse(self.path)
        path = p.path
        params = urllib.parse.parse_qs(p.query)

        if path in ("/", "/index.html"):
            self._static("index.html", "text/html; charset=utf-8")
        elif path == "/style.css":
            self._static("style.css", "text/css")
        elif path == "/app.js":
            self._static("app.js", "application/javascript")
        elif path == "/api/tasks":
            tasks = load_tasks()
            status   = params.get("status",   [None])[0]
            priority = params.get("priority", [None])[0]
            search   = params.get("search",   [None])[0]
            if status and status != "all":
                tasks = [t for t in tasks if t["status"] == status]
            if priority and priority != "all":
                tasks = [t for t in tasks if t["priority"] == priority]
            if search:
                q = search.lower()
                tasks = [t for t in tasks
                         if q in t["title"].lower() or q in t.get("description","").lower()]
            self._json(200, tasks)
        elif path == "/api/stats":
            tasks = load_tasks()
            self._json(200, {
                "total":       len(tasks),
                "pending":     sum(1 for t in tasks if t["status"] == "pending"),
                "in_progress": sum(1 for t in tasks if t["status"] == "in_progress"),
                "completed":   sum(1 for t in tasks if t["status"] == "completed"),
                "high":        sum(1 for t in tasks if t["priority"] == "high"),
            })
        else:
            self._json(404, {"error": "Not found"})

    def do_POST(self):
        if self.path == "/api/tasks":
            body = self._body()
            title = body.get("title", "").strip()
            if not title:
                self._json(400, {"error": "Title required"}); return
            tasks = load_tasks()
            task = {
                "id":          next_id(tasks),
                "title":       title,
                "description": body.get("description", "").strip(),
                "priority":    body.get("priority", "medium"),
                "status":      "pending",
                "due_date":    body.get("due_date", ""),
                "created_at":  datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            tasks.append(task)
            save_tasks(tasks)
            self._json(201, task)
        else:
            self._json(404, {"error": "Not found"})

    def do_PUT(self):
        parts = self.path.strip("/").split("/")
        if len(parts) == 3 and parts[0] == "api" and parts[1] == "tasks":
            try:
                tid = int(parts[2])
            except ValueError:
                self._json(400, {"error": "Bad ID"}); return
            body  = self._body()
            tasks = load_tasks()
            for t in tasks:
                if t["id"] == tid:
                    for k in ["title","description","priority","status","due_date"]:
                        if k in body:
                            t[k] = body[k]
                    t["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    save_tasks(tasks)
                    self._json(200, t); return
            self._json(404, {"error": "Task not found"})
        else:
            self._json(404, {"error": "Not found"})

    def do_DELETE(self):
        parts = self.path.strip("/").split("/")
        if len(parts) == 3 and parts[0] == "api" and parts[1] == "tasks":
            try:
                tid = int(parts[2])
            except ValueError:
                self._json(400, {"error": "Bad ID"}); return
            tasks = load_tasks()
            new   = [t for t in tasks if t["id"] != tid]
            if len(new) == len(tasks):
                self._json(404, {"error": "Not found"}); return
            save_tasks(new)
            self._json(200, {"ok": True})
        else:
            self._json(404, {"error": "Not found"})

    def log_message(self, fmt, *args):
        print(f"  [{datetime.now().strftime('%H:%M:%S')}] {fmt % args}")

# ─── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    PORT = 8000
    httpd = HTTPServer(("localhost", PORT), Handler)
    print("=" * 50)
    print("  TaskFlow Server Started!")
    print(f"  Open in browser: http://localhost:{PORT}")
    print("  Stop with Ctrl+C")
    print("=" * 50)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n  Server stopped.")
        httpd.server_close()