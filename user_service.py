import tornado.web
import tornado.options
import sqlite3
import time
import json

class BaseHandler(tornado.web.RequestHandler):
    def write_json(self, data=None, status=200, message="Success", start_time=None):
        self.set_header("Content-Type", "application/json")
        self.set_status(status)
        timestamp = int(time.time() * 1000)
        execution_time_ms = int((time.time() - start_time) * 1000) if start_time else None
        response = {
            "status": status,
            "message": message,
            "timestamp": timestamp,
            "execution_time_ms": execution_time_ms,
            "data": data
        }
        self.write(json.dumps(response))

class App(tornado.web.Application):
    def __init__(self, handlers, **kwargs):
        super().__init__(handlers, **kwargs)
        self.db = sqlite3.connect("users.db")
        self.db.row_factory = sqlite3.Row
        self.init_db()

    def init_db(self):
        cursor = self.db.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                created_at INTEGER NOT NULL,
                updated_at INTEGER NOT NULL
            );
        """)
        self.db.commit()

class UsersHandler(BaseHandler):
    def get(self):
        start_time = time.time()
        page_num = int(self.get_argument("page_num", 1))
        page_size = int(self.get_argument("page_size", 10))
        offset = (page_num - 1) * page_size

        cursor = self.application.db.cursor()
        cursor.execute(
            "SELECT * FROM users ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (page_size, offset)
        )
        rows = cursor.fetchall()
        users = [dict(r) for r in rows]
        self.write_json(data={"users": users}, status=200, message="Users fetched successfully", start_time=start_time)

    def post(self):
        start_time = time.time()
        try:
            name = self.get_argument("name")
            now = int(time.time() * 1e6)
            cursor = self.application.db.cursor()
            cursor.execute(
                "INSERT INTO users (name, created_at, updated_at) VALUES (?, ?, ?)",
                (name, now, now)
            )
            self.application.db.commit()
            user = dict(id=cursor.lastrowid, name=name, created_at=now, updated_at=now)
            self.write_json(data={"user": user}, status=201, message="User created successfully", start_time=start_time)
        except Exception as e:
            self.write_json(data=None, status=500, message=f"Error creating user: {e}", start_time=start_time)

class UserDetailHandler(BaseHandler):
    def get(self, user_id):
        start_time = time.time()
        cursor = self.application.db.cursor()
        row = cursor.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
        if not row:
            self.write_json(data=None, status=404, message="User not found", start_time=start_time)
            return
        self.write_json(data={"user": dict(row)}, status=200, message="User fetched successfully", start_time=start_time)

class PingHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("pong!")

def make_app(options):
    return App([
        (r"/users/ping", PingHandler),
        (r"/users", UsersHandler),
        (r"/users/([0-9]+)", UserDetailHandler),
    ], debug=options.debug)

if __name__ == "__main__":
    tornado.options.define("port", default=8001)
    tornado.options.define("debug", default=True)
    tornado.options.parse_command_line()
    options = tornado.options.options

    app = make_app(options)
    app.listen(options.port)
    print(f"User service running on PORT {options.port}")
    tornado.ioloop.IOLoop.current().start()
