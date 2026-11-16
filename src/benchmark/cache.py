from __future__ import annotations
import hashlib, json, sqlite3, time
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS responses (
  cache_key TEXT PRIMARY KEY, task_id TEXT, provider TEXT, model_id TEXT, prompt_version TEXT,
  gen_config TEXT, prompt_hash TEXT, response TEXT, input_tokens INTEGER, output_tokens INTEGER,
  latency_ms REAL, status TEXT, error TEXT, meta TEXT, created_at TEXT)
"""


class ResponseCache:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute(SCHEMA)
        self.conn.commit()

    @staticmethod
    def make_key(task_id, provider, model_id, prompt_version, gen_config, prompt_hash) -> str:
        blob = json.dumps([task_id, provider, model_id, prompt_version, gen_config, prompt_hash], sort_keys=True)
        return hashlib.sha256(blob.encode()).hexdigest()

    def get(self, key):
        r = self.conn.execute("SELECT * FROM responses WHERE cache_key=?", (key,)).fetchone()
        return dict(r) if r else None

    def get_success(self, key):
        r = self.get(key)
        return r if r and r["status"] == "ok" else None

    def put(self, key, task_id, provider, model_id, prompt_version, gen_config, prompt_hash, result):
        """Saves immediately. A stored success is never overwritten by a later error."""
        row = (key, task_id, provider, model_id, prompt_version, json.dumps(gen_config, sort_keys=True), prompt_hash,
               result.text, result.input_tokens, result.output_tokens, result.latency_ms, result.status,
               result.error, json.dumps(result.meta), time.strftime("%Y-%m-%dT%H:%M:%S%z"))
        self.conn.execute(
            """INSERT INTO responses VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
               ON CONFLICT(cache_key) DO UPDATE SET response=excluded.response, input_tokens=excluded.input_tokens,
               output_tokens=excluded.output_tokens, latency_ms=excluded.latency_ms, status=excluded.status,
               error=excluded.error, meta=excluded.meta, created_at=excluded.created_at
               WHERE responses.status != 'ok'""", row)
        self.conn.commit()

    def count(self, status="ok"):
        return self.conn.execute("SELECT COUNT(*) FROM responses WHERE status=?", (status,)).fetchone()[0]
