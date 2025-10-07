import tornado.web
import tornado.options
import requests
import time
import json

LISTING_SERVICE_URL = "http://localhost:8000"
USER_SERVICE_URL = "http://localhost:8001"

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

class PublicListingsHandler(BaseHandler):
    def get(self):
        start_time = time.time()
        params = {
            "page_num": self.get_argument("page_num", 1),
            "page_size": self.get_argument("page_size", 10)
        }
        user_id = self.get_argument("user_id", None)
        if user_id:
            params["user_id"] = user_id
        try:
            resp = requests.get(f"{LISTING_SERVICE_URL}/listings", params=params)
            data = resp.json().get("data", {})
        except Exception as e:
            self.write_json(data=None, status=500, message=f"Failed to connect to Listing Service: {e}", start_time=start_time)
            return

        for listing in data.get("listings", []):
            try:
                user_resp = requests.get(f"{USER_SERVICE_URL}/users/{listing['user_id']}")
                if user_resp.status_code == 200:
                    listing["user"] = user_resp.json().get("data", {}).get("user")
                else:
                    listing["user"] = None
            except Exception:
                listing["user"] = None

        self.write_json(data={"listings": data.get("listings", [])}, status=200, message="Public listings fetched", start_time=start_time)

    def post(self):
        start_time = time.time()
        try:
            body = json.loads(self.request.body)
            resp = requests.post(f"{LISTING_SERVICE_URL}/listings", data=body)
            self.write_json(data=resp.json().get("data"), status=resp.status_code, message="Listing created", start_time=start_time)
        except Exception as e:
            self.write_json(data=None, status=500, message=f"Failed to create listing: {e}", start_time=start_time)

class PublicUsersHandler(BaseHandler):
    def post(self):
        start_time = time.time()
        try:
            body = json.loads(self.request.body)
            resp = requests.post(f"{USER_SERVICE_URL}/users", data=body)
            self.write_json(data=resp.json().get("data"), status=resp.status_code, message="User created", start_time=start_time)
        except Exception as e:
            self.write_json(data=None, status=500, message=f"Failed to create user: {e}", start_time=start_time)

class PingHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("pong!")

def make_app(options):
    return tornado.web.Application([
        (r"/public-api/ping", PingHandler),
        (r"/public-api/listings", PublicListingsHandler),
        (r"/public-api/users", PublicUsersHandler),
    ], debug=options.debug)

if __name__ == "__main__":
    tornado.options.define("port", default=8002)
    tornado.options.define("debug", default=True)
    tornado.options.parse_command_line()
    options = tornado.options.options

    app = make_app(options)
    app.listen(options.port)
    print(f"Public API running on PORT {options.port}")
    tornado.ioloop.IOLoop.instance().start()
