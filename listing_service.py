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
        self.db = sqlite3.connect("listings.db")
        self.db.row_factory = sqlite3.Row
        self.init_db()

    def init_db(self):
        cursor = self.db.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS listings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                listing_type TEXT NOT NULL,
                price INTEGER NOT NULL,
                created_at INTEGER NOT NULL,
                updated_at INTEGER NOT NULL
            );
        """)
        self.db.commit()

class ListingsHandler(BaseHandler):
    def get(self):
        start_time = time.time()
        page_num = int(self.get_argument("page_num", 1))
        page_size = int(self.get_argument("page_size", 10))
        user_id = self.get_argument("user_id", None)
        offset = (page_num - 1) * page_size

        cursor = self.application.db.cursor()
        if user_id:
            cursor.execute(
                "SELECT * FROM listings WHERE user_id=? ORDER BY created_at DESC LIMIT ? OFFSET ?",
                (user_id, page_size, offset)
            )
        else:
            cursor.execute(
                "SELECT * FROM listings ORDER BY created_at DESC LIMIT ? OFFSET ?",
                (page_size, offset)
            )

        rows = cursor.fetchall()
        listings = [dict(r) for r in rows]
        self.write_json(data={"listings": listings}, status=200, message="Listings fetched successfully", start_time=start_time)

    def post(self):
        start_time = time.time()
        try:
            user_id = int(self.get_argument("user_id"))
            listing_type = self.get_argument("listing_type")
            price = int(self.get_argument("price"))
            now = int(time.time() * 1e6)

            cursor = self.application.db.cursor()
            cursor.execute(
                "INSERT INTO listings (user_id, listing_type, price, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                (user_id, listing_type, price, now, now)
            )
            self.application.db.commit()

            listing = dict(
                id=cursor.lastrowid,
                user_id=user_id,
                listing_type=listing_type,
                price=price,
                created_at=now,
                updated_at=now
            )
            self.write_json(data={"listing": listing}, status=201, message="Listing created successfully", start_time=start_time)
        except Exception as e:
            self.write_json(data=None, status=500, message=f"Error creating listing: {e}", start_time=start_time)

class PingHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("pong!")

def make_app(options):
    return App([
        (r"/listings/ping", PingHandler),
        (r"/listings", ListingsHandler),
    ], debug=options.debug)

if __name__ == "__main__":
    tornado.options.define("port", default=8000)
    tornado.options.define("debug", default=True)
    tornado.options.parse_command_line()
    options = tornado.options.options

    app = make_app(options)
    app.listen(options.port)
    print(f"Listing service running on PORT {options.port}")
    tornado.ioloop.IOLoop.instance().start()
