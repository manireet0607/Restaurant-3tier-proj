# Dragon Wok 🐉

A Chinese restaurant web app. Customers browse the menu, fill a cart, place Cash on Delivery orders and see their order history. Admins manage food items, categories and orders.

## 1. Three-tier architecture

```
 Browser ──► Frontend (React, served by Nginx)      Presentation tier
                │  REST / JSON  (/api/v1)
                ▼
            Backend (Python, FastAPI)               Application tier
                │  SQLAlchemy (TLS to RDS)
                ▼
            MySQL 8 (local container or Amazon RDS) Data tier
```

The three parts are separate and only talk through these interfaces. The browser never sees database credentials or the secret key.

## 2. Technology stack

| Tier | Tools |
|---|---|
| Frontend | React 18, React Router, Vite, plain CSS |
| Backend | Python 3.12, FastAPI, SQLAlchemy 2, Pydantic v2, Alembic, PyJWT, bcrypt |
| Database | MySQL 8 (Amazon RDS for MySQL in production) |
| Tests | pytest, FastAPI TestClient (SQLite test database) |
| Packaging | Docker, Docker Compose |

## 3. Folder structure

```
dragon-wok/
├── frontend/            React app (src/components, pages, services, context, hooks)
├── backend/
│   ├── app/             api/ core/ models/ schemas/ services/ db/ main.py
│   ├── alembic/         database migrations
│   └── tests/           pytest tests
├── database/init.sql    optional hand-run schema + sample data
├── docker-compose.yml   frontend + backend + local MySQL
├── .env.example
└── README.md
```

## 4. Prerequisites

- Docker and Docker Compose (easiest), **or** Python 3.12+, Node 20+ and a MySQL 8 server.

## 5. Quick start with Docker Compose

```bash
cp .env.example .env
# Edit .env: set DB_PASSWORD, DB_ROOT_PASSWORD, SECRET_KEY and ADMIN_PASSWORD
docker compose up --build
```

- Website: http://localhost:3000
- API docs: http://localhost:8000/docs (disabled when `APP_ENV=production`)
- On start the backend runs the migrations, adds the sample menu, and creates the admin user (if `ADMIN_PASSWORD` is set). Log in at `/login` with `ADMIN_EMAIL` and `ADMIN_PASSWORD`.
- MySQL data is kept in the `mysql_data` volume. The database port is bound to `127.0.0.1:3307` only. Remove that `ports` block if you do not need it.

## 6. Local install without Docker

Backend:
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export DB_HOST=localhost DB_USER=dragonwok DB_PASSWORD=... DB_NAME=dragonwok SECRET_KEY=... ADMIN_PASSWORD=...
alembic upgrade head          # create tables
python -m app.db.seed         # sample menu + admin user
uvicorn app.main:app --reload # http://localhost:8000
```
Frontend:
```bash
cd frontend
cp .env.example .env          # VITE_API_URL=http://localhost:8000/api/v1
npm install
npm run dev                   # http://localhost:5173
```
Create the empty database first: `CREATE DATABASE dragonwok CHARACTER SET utf8mb4;`

## 7. Environment variables

See `.env.example`. The important ones:

| Variable | Meaning |
|---|---|
| `APP_ENV` | `development` or `production`. Production needs a `SECRET_KEY` of 32+ characters and turns off `/docs`. |
| `SECRET_KEY` | Signs login tokens. Generate: `python -c "import secrets; print(secrets.token_urlsafe(48))"` |
| `CORS_ORIGINS` | Comma separated list of frontend URLs allowed to call the API. |
| `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` | Database connection (local MySQL or RDS). |
| `DB_SSL_CA` | Path to the RDS CA bundle. When set, the certificate and host name are verified. |
| `DELIVERY_FEE`, `TAX_PERCENT` | Order fee settings (defaults ₹40 and 5%). |
| `ADMIN_EMAIL`, `ADMIN_PASSWORD` | First admin, created by the seed script. |
| `VITE_API_URL` | Backend URL used by the frontend (set at build time). |

## 8. Database and migrations

Tables: `users`, `categories`, `menu_items`, `orders`, `order_items`. Money is `DECIMAL(10,2)`. `order_items.unit_price` stores the price at order time, so old orders never change when menu prices change. Foreign keys, indexes and check constraints are in the migration.

```bash
cd backend
alembic upgrade head                       # apply
alembic revision --autogenerate -m "name"  # new migration after changing models
alembic downgrade -1                       # undo last
python -m app.db.seed                      # safe to run many times
```

`database/init.sql` is an alternative for setting up by hand. **Use either Alembic or `init.sql`, not both.** If you used `init.sql`, run `alembic stamp head` so Alembic knows the schema exists.

## 9. API (`/api/v1`)

Auth uses `Authorization: Bearer <token>`.

| Method | Path | Who | What |
|---|---|---|---|
| POST | `/auth/register` | public | Create customer account, returns token |
| POST | `/auth/login` | public | Login, returns token |
| GET | `/users/me` | customer | Own profile |
| GET | `/categories` | public | List categories |
| GET | `/menu?category_id=` | public | List food items |
| GET | `/config` | public | Delivery fee and tax % (display only) |
| POST | `/orders` | customer | Place an order |
| GET | `/orders` | customer | Own orders |
| GET | `/orders/{id}` | customer/admin | One order (customers: own only) |
| GET | `/admin/stats` | admin | Orders, revenue, customers, menu items |
| GET | `/admin/customers` | admin | Customer list |
| POST/PUT/DELETE | `/admin/categories[/{id}]` | admin | Manage categories |
| POST/PUT/DELETE | `/admin/menu[/{id}]` | admin | Manage food items |
| PATCH | `/admin/menu/{id}/availability` | admin | Turn availability on/off |
| GET | `/admin/orders?status=&limit=&offset=` | admin | All orders |
| PATCH | `/admin/orders/{id}/status` | admin | Change order status |
| GET | `/health` (no prefix) | public | Liveness check |
| GET | `/api/v1/health` | public | Readiness check (tests the database) |

`POST /orders` body (only these fields are accepted; anything else returns 422):
```json
{ "customer_name": "Asha", "customer_phone": "9876543210",
  "delivery_address": "12 MG Road, New Delhi", "special_instructions": "No onion",
  "payment_method": "cod", "items": [{ "menu_item_id": 1, "quantity": 2 }] }
```

Errors use normal HTTP codes: 400, 401, 403, 404, 409, 422, 500. Messages never include internal details.

### Order rules
`pending → confirmed → preparing → out_for_delivery → delivered`. Cancel is allowed from pending, confirmed and preparing. Skipping steps or changing a finished order returns 409. The server calculates subtotal, delivery fee, tax and total from current database prices. The client cannot send prices, totals or a status. For Cash on Delivery, `payment_status` becomes `paid` when the order is delivered.

Payments are modular: `backend/app/services/payments.py` has a `PaymentProvider` interface. Add an online gateway by writing a new provider and registering it.

## 10. Tests

```bash
cd backend
pytest -q
```
The tests use a temporary SQLite file, so no MySQL is needed. They cover registration and login, authorization, menu, order creation and totals, invalid orders, admin menu management and status changes.

## 11. AWS deployment (nothing is created automatically)

Suggested layout:

- **Database:** Amazon RDS for MySQL 8, **private subnets**, "Publicly accessible = No". Security group: allow port 3306 **only from the backend's security group**.
- **Backend:** Amazon ECS (Fargate) or EC2 running the `backend` Docker image, in private subnets behind an Application Load Balancer. Health check path: `/health`.
- **Frontend:** `cd frontend && VITE_API_URL=https://api.example.com/api/v1 npm run build`, upload `dist/` to S3, serve with CloudFront (HTTPS). Set the error page for 403/404 to `/index.html` so page links work. Or run the `frontend` image on ECS.
- **Secrets:** store `SECRET_KEY`, `DB_PASSWORD`, `ADMIN_PASSWORD` in AWS Secrets Manager or SSM Parameter Store and inject them as environment variables. Never put them in the image or in Git.

Steps:
1. Create the RDS instance and the security groups above.
2. Build and push the backend image to Amazon ECR.
3. Create the ECS task / EC2 service with these environment variables: `APP_ENV=production`, `SECRET_KEY`, `DB_HOST` (RDS endpoint), `DB_USER`, `DB_PASSWORD`, `DB_NAME`, `DB_SSL_CA=/certs/global-bundle.pem`, `CORS_ORIGINS=https://your-frontend-domain`, `ADMIN_PASSWORD` (first run only).
4. The container runs `alembic upgrade head` and the seed script on start, then serves the API. For several instances, run migrations as a one-off task instead.
5. Deploy the frontend to S3 + CloudFront.
6. Put HTTPS on the load balancer (ACM certificate).

**RDS TLS:** the backend Docker image already contains the AWS RDS CA bundle at `/certs/global-bundle.pem`. Setting `DB_SSL_CA` turns on certificate and host name verification. Use the RDS endpoint name as `DB_HOST` (not an IP) so the host name check passes.

**Logging:** the backend writes JSON logs to stdout. With ECS use the `awslogs` log driver; on EC2 use the CloudWatch agent.

**Environments:** keep separate `.env` files or secret sets for development and production. `APP_ENV=production` also refuses weak secret keys and hides the API docs.

## 12. Security notes

- Passwords are hashed with bcrypt. Plain passwords are never stored or logged.
- Login tokens (JWT) expire after `ACCESS_TOKEN_EXPIRE_MINUTES` (default 60).
- Roles are checked on the server for every admin route, using the role in the database.
- Public registration can only create customers. Admins come from the seed script.
- Order totals are always calculated on the server. Unknown request fields are rejected.
- All database access goes through SQLAlchemy with bound parameters.
- CORS allows only the origins you list.
- Secrets come from environment variables. `.env` is in `.gitignore`.
- Error responses are generic. Details go to the logs only.
- The frontend keeps the token in `localStorage`. This is simple, but any XSS bug could read it. The app does not render raw HTML. For stricter setups, move to httpOnly cookies.
- Not included, add before a busy production launch: rate limiting on login (for example at the load balancer or AWS WAF), password reset by email, token refresh.

## 13. Troubleshooting

| Problem | Fix |
|---|---|
| Frontend shows "Cannot reach the server" | Check the backend is running and `VITE_API_URL` is right. Rebuild the frontend after changing it. |
| Browser CORS error | Add the frontend URL to `CORS_ORIGINS` (exact match, no trailing slash) and restart the backend. |
| `Can't connect to MySQL server` in Docker | Wait for the `db` health check, or run `docker compose logs db`. |
| `SSL: CERTIFICATE_VERIFY_FAILED` with RDS | Use the RDS endpoint name for `DB_HOST` and make sure `DB_SSL_CA` points to the AWS bundle. |
| `Access denied for user` | Check `DB_USER` / `DB_PASSWORD`. Changing `.env` does not change an existing MySQL volume: run `docker compose down -v` (this deletes local data). |
| `Table already exists` on `alembic upgrade` | You used `init.sql` before. Run `alembic stamp head`. |
| Can't log in as admin | `ADMIN_PASSWORD` must be set before the first seed run. The seed does not change an existing admin. |
| Production start fails with "Set a strong SECRET_KEY" | Set a `SECRET_KEY` of 32+ random characters. |
| Food images look like drawings | The sample images are simple placeholders in `frontend/public/images`. Replace them, or set real image URLs in the admin dashboard. |
