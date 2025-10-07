<h1 align="center">Multi-Service Tornado API</h1>

<p align="center">
  Example implementation of <strong>microservices</strong> using <strong>Python Tornado</strong> and <strong>SQLite</strong>.
</p>

---

<h2>Services</h2>
<ul>
  <li><strong>Listing Service</strong> (<code>port 8000</code>) – Manages listings.</li>
  <li><strong>User Service</strong> (<code>port 8001</code>) – Manages users.</li>
  <li><strong>Public API</strong> (<code>port 8002</code>) – Public API combining Listing & User Services.</li>
</ul>

---

<h2>Features</h2>
<ul>
  <li>CRUD for <strong>Listings</strong> and <strong>Users</strong>.</li>
  <li>Pagination support for <code>GET</code> endpoints.</li>
  <li>Standard JSON response structure:
    <ul>
      <li><code>status</code></li>
      <li><code>message</code></li>
      <li><code>timestamp</code></li>
      <li><code>execution_time_ms</code></li>
      <li><code>data</code></li>
    </ul>
  </li>
  <li>Health check ping endpoints.</li>
  <li>Public API fetches listings with user info from other services.</li>
</ul>

---

<h2>Project Structure</h2>
<pre>
multi-service-tornado-api/
├── listing_service.py      # Service untuk CRUD Listings (port 8000)
├── user_service.py         # Service untuk CRUD Users (port 8001)
├── public_api.py           # Public API gateway (port 8002), fetches data dari Listing & User Services
├── listings.db             # SQLite database untuk Listings (auto-created)
├── users.db                # SQLite database untuk Users (auto-created)
├── README.md               # Dokumentasi project ini
└── requirements.txt        # File optional, untuk dependencies Python (tornado, requests)
</pre>

---

<h2>Installation</h2>
<pre>
git clone &lt;repo-url&gt;
cd &lt;project-folder&gt;

python3 -m venv env
source env/bin/activate
pip install tornado requests
</pre>

---

<h2>Running Services</h2>
<ul>
  <li><strong>Listing Service</strong> – <code>http://localhost:8000</code>
    <pre>python listing_service.py --port=8000 --debug=True</pre>
  </li>
  <li><strong>User Service</strong> – <code>http://localhost:8001</code>
    <pre>python user_service.py --port=8001 --debug=True</pre>
  </li>
  <li><strong>Public API</strong> – <code>http://localhost:8002</code>
    <pre>python public_api.py --port=8002 --debug=True</pre>
  </li>
</ul>

---

<h2>Endpoints & Example Requests</h2>

<h3>Listing Service (CRUD)</h3>
<table>
<tr><th>Method</th><th>Endpoint</th><th>Description</th><th>Example Request</th></tr>
<tr>
<td>GET</td><td>/listings</td>
<td>Get all listings (pagination, optional user_id filter)</td>
<td><pre>curl "http://localhost:8000/listings?page_num=1&page_size=5&user_id=1"</pre></td>
</tr>
<tr>
<td>POST</td><td>/listings</td>
<td>Create a new listing</td>
<td><pre>curl -X POST "http://localhost:8000/listings" -d "user_id=1&listing_type=house&price=100000"</pre></td>
</tr>
<tr>
<td>GET</td><td>/listings/{id}</td>
<td>Get a listing by ID</td>
<td><pre>curl "http://localhost:8000/listings/1"</pre></td>
</tr>
<tr>
<td>PUT</td><td>/listings/{id}</td>
<td>Update a listing by ID</td>
<td><pre>curl -X PUT "http://localhost:8000/listings/1" -d "listing_type=apartment&price=120000"</pre></td>
</tr>
<tr>
<td>DELETE</td><td>/listings/{id}</td>
<td>Delete a listing by ID</td>
<td><pre>curl -X DELETE "http://localhost:8000/listings/1"</pre></td>
</tr>
<tr>
<td>GET</td><td>/listings/ping</td>
<td>Health check</td>
<td><pre>curl "http://localhost:8000/listings/ping"</pre></td>
</tr>
</table>

<h3>User Service (CRUD)</h3>
<table>
<tr><th>Method</th><th>Endpoint</th><th>Description</th><th>Example Request</th></tr>
<tr>
<td>GET</td><td>/users</td>
<td>List all users (pagination)</td>
<td><pre>curl "http://localhost:8001/users?page_num=1&page_size=5"</pre></td>
</tr>
<tr>
<td>POST</td><td>/users</td>
<td>Create a new user</td>
<td><pre>curl -X POST "http://localhost:8001/users" -d "name=John Doe"</pre></td>
</tr>
<tr>
<td>GET</td><td>/users/{id}</td>
<td>Get user details by ID</td>
<td><pre>curl "http://localhost:8001/users/1"</pre></td>
</tr>
<tr>
<td>PUT</td><td>/users/{id}</td>
<td>Update a user by ID</td>
<td><pre>curl -X PUT "http://localhost:8001/users/1" -d "name=Jane Doe"</pre></td>
</tr>
<tr>
<td>DELETE</td><td>/users/{id}</td>
<td>Delete a user by ID</td>
<td><pre>curl -X DELETE "http://localhost:8001/users/1"</pre></td>
</tr>
<tr>
<td>GET</td><td>/users/ping</td>
<td>Health check</td>
<td><pre>curl "http://localhost:8001/users/ping"</pre></td>
</tr>
</table>

<h3>Public API</h3>
<table>
<tr><th>Method</th><th>Endpoint</th><th>Description</th><th>Example Request</th></tr>
<tr>
<td>GET</td><td>/public-api/listings</td>
<td>Fetch listings with user info</td>
<td><pre>curl "http://localhost:8002/public-api/listings?page_num=1&page_size=5&user_id=1"</pre></td>
</tr>
<tr>
<td>POST</td><td>/public-api/listings</td>
<td>Create a listing via Public API</td>
<td><pre>curl -X POST "http://localhost:8002/public-api/listings" -H "Content-Type: application/json" -d '{"user_id":1,"listing_type":"house","price":100000}'</pre></td>
</tr>
<tr>
<td>PUT</td><td>/public-api/listings/{id}</td>
<td>Update listing via Public API</td>
<td><pre>curl -X PUT "http://localhost:8002/public-api/listings/1" -H "Content-Type: application/json" -d '{"listing_type":"apartment","price":120000}'</pre></td>
</tr>
<tr>
<td>DELETE</td><td>/public-api/listings/{id}</td>
<td>Delete listing via Public API</td>
<td><pre>curl -X DELETE "http://localhost:8002/public-api/listings/1"</pre></td>
</tr>
<tr>
<td>POST</td><td>/public-api/users</td>
<td>Create a user via Public API</td>
<td><pre>curl -X POST "http://localhost:8002/public-api/users" -H "Content-Type: application/json" -d '{"name":"John Doe"}'</pre></td>
</tr>
<tr>
<td>PUT</td><td>/public-api/users/{id}</td>
<td>Update user via Public API</td>
<td><pre>curl -X PUT "http://localhost:8002/public-api/users/1" -H "Content-Type: application/json" -d '{"name":"Jane Doe"}'</pre></td>
</tr>
<tr>
<td>DELETE</td><td>/public-api/users/{id}</td>
<td>Delete user via Public API</td>
<td><pre>curl -X DELETE "http://localhost:8002/public-api/users/1"</pre></td>
</tr>
<tr>
<td>GET</td><td>/public-api/ping</td>
<td>Public API health check</td>
<td><pre>curl "http://localhost:8002/public-api/ping"</pre></td>
</tr>
</table>

---

<h2>Example JSON Response</h2>
<pre>
{
  "status": 200,
  "message": "Listings fetched successfully",
  "timestamp": 1700000000000,
  "execution_time_ms": 15,
  "data": {
    "listings": [
      {
        "id": 1,
        "user_id": 1,
        "listing_type": "house",
        "price": 100000,
        "created_at": 1700000000000,
        "updated_at": 1700000000000,
        "user": {
          "id": 1,
          "name": "John Doe",
          "created_at": 1700000000000,
          "updated_at": 1700000000000
        }
      }
    ]
  }
}
</pre>

---

<h2>Notes</h2>
<ul>
  <li>SQLite databases are created automatically when services start.</li>
  <li>Timestamps are stored in <strong>microseconds</strong>.</li>
  <li>Public API fetches data from Listing & User Services using <code>requests</code>.</li>
</ul>

<h2>License</h2>
<p>MIT License</p>
