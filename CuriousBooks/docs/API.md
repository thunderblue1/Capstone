# CuriousBooks API Reference

Base URL: `http://localhost:5000/api` (or set via `VITE_API_URL`).

When `API_KEY` is set on the server, include header: `X-API-Key: <your-api-key>` on all `/api/*` requests (except health and Stripe webhook).  
For authenticated endpoints, also send: `Authorization: Bearer <access_token>`.

---

## General

| Route | Method | Description |
|-------|--------|-------------|
| `/` | GET | Welcome and list of API sections. |
| `/api/health` | GET | Health check. |

### Example: GET /

```json
{
  "message": "Welcome to CuriousBooks API",
  "version": "1.0.0",
  "docs": "/api/docs",
  "endpoints": {
    "books": "/api/books",
    "categories": "/api/categories",
    "auth": "/api/auth",
    "reviews": "/api/reviews",
    "orders": "/api/orders",
    "recommendations": "/api/recommendations"
  }
}
```

### Example: GET /api/health

```json
{
  "status": "healthy",
  "service": "CuriousBooks API",
  "version": "1.0.0"
}
```

---

## Books

| Route | Method | Description |
|-------|--------|-------------|
| `/api/books` | GET | List books with pagination and filters (category, genre, price, in_stock, sort). |
| `/api/books` | POST | Create a book (manager only, JWT required). |
| `/api/books/featured` | GET | Featured/popular books for homepage. |
| `/api/books/search` | GET | Search by title, author, description, genre, or ISBN. |
| `/api/books/category/<name>` | GET | Books in a category by name. |
| `/api/books/<id>` | GET | Single book by ID. |
| `/api/books/<id>` | PUT | Update a book (manager only, JWT required). |
| `/api/books/<id>` | DELETE | Delete a book (manager only, JWT required). |
| `/api/books/<id>/reviews` | GET | Paginated reviews for a book. |
| `/api/books/genres` | GET | All unique genres. |

### Example: GET /api/books

Query: `page`, `per_page`, `category_id`, `genre`, `min_price`, `max_price`, `in_stock`, `sort_by`, `sort_order`.

```json
{
  "books": [
    {
      "id": 1,
      "title": "Example Book",
      "author": "Author Name",
      "description": "...",
      "price": "19.99",
      "genre": "Fiction",
      "stock_quantity": 10,
      "average_rating": 4.5,
      "review_count": 12,
      "popularity_score": 100,
      "category_id": 1,
      "isbn_13": "978-0-00-000000-0",
      "created_at": "2024-01-01T00:00:00"
    }
  ],
  "total": 150,
  "pages": 8,
  "currentPage": 1,
  "perPage": 20,
  "hasNext": true,
  "hasPrev": false
}
```

### Example: GET /api/books/featured

Query: `limit` (default 4).

```json
{
  "books": [
    { "id": 1, "title": "...", "author": "...", "price": "19.99", "average_rating": 4.5, "genre": "Fiction", "stock_quantity": 10, "popularity_score": 100, "category_id": 1, "review_count": 5, "description": "...", "isbn_13": "...", "created_at": "..." }
  ]
}
```

### Example: GET /api/books/search

Query: `q` (required), `page`, `per_page`.

```json
{
  "results": [
    { "id": 1, "title": "...", "author": "...", "price": "19.99", "genre": "Fiction", "stock_quantity": 10, "average_rating": 4.5, "review_count": 5, "popularity_score": 100, "category_id": 1, "description": "...", "isbn_13": "...", "created_at": "..." }
  ],
  "total": 5,
  "pages": 1,
  "currentPage": 1,
  "query": "search term"
}
```

### Example: GET /api/books/<id>

```json
{
  "id": 1,
  "title": "Example Book",
  "author": "Author Name",
  "description": "...",
  "price": "19.99",
  "genre": "Fiction",
  "stock_quantity": 10,
  "average_rating": 4.5,
  "review_count": 12,
  "popularity_score": 100,
  "category_id": 1,
  "category": { "id": 1, "name": "Fiction", "slug": "fiction" },
  "isbn_13": "978-0-00-000000-0",
  "created_at": "2024-01-01T00:00:00"
}
```

### Example: GET /api/books/<id>/reviews

Query: `page`, `per_page`.

```json
{
  "reviews": [
    {
      "id": 1,
      "book_id": 1,
      "user_id": 1,
      "rating": 4.5,
      "comment": "Great read.",
      "created_at": "2024-01-15T12:00:00",
      "user": { "id": 1, "username": "johndoe" }
    }
  ],
  "total": 12,
  "pages": 2,
  "currentPage": 1,
  "averageRating": 4.5,
  "reviewCount": 12
}
```

### Example: GET /api/books/genres

```json
{
  "genres": ["Fiction", "Non-Fiction", "Science", "Mystery"]
}
```

---

## Categories

| Route | Method | Description |
|-------|--------|-------------|
| `/api/categories` | GET | List categories (optional: root_only, include_subcategories). |
| `/api/categories/<id>` | GET | Single category by ID. |
| `/api/categories/<id>/books` | GET | Books in category with pagination. |
| `/api/categories/name/<name>` | GET | Category by name (case-insensitive). |

### Example: GET /api/categories

Query: `root_only`, `include_subcategories`.

```json
{
  "categories": [
    {
      "id": 1,
      "name": "Fiction",
      "slug": "fiction",
      "parent_id": null,
      "subcategories": []
    }
  ]
}
```

### Example: GET /api/categories/<id>

```json
{
  "id": 1,
  "name": "Fiction",
  "slug": "fiction",
  "parent_id": null,
  "parent": null,
  "subcategories": []
}
```

### Example: GET /api/categories/<id>/books

Query: `page`, `per_page`.

```json
{
  "category": { "id": 1, "name": "Fiction", "slug": "fiction" },
  "books": [
    { "id": 1, "title": "...", "author": "...", "price": "19.99", "genre": "Fiction", "stock_quantity": 10, "average_rating": 4.5, "review_count": 5, "popularity_score": 100, "category_id": 1, "description": "...", "isbn_13": "...", "created_at": "..." }
  ],
  "total": 50,
  "pages": 3,
  "currentPage": 1
}
```

---

## Authentication

| Route | Method | Description |
|-------|--------|-------------|
| `/api/auth/register` | POST | Register a new user. |
| `/api/auth/login` | POST | Login; returns access and refresh tokens. |
| `/api/auth/refresh` | POST | Refresh access token (send refresh token in Authorization). |
| `/api/auth/me` | GET | Current user profile (JWT required). |
| `/api/auth/me` | PUT | Update current user profile (JWT required). |
| `/api/auth/change-password` | POST | Change password (JWT required). |

### Example: POST /api/auth/register

Request body:

```json
{
  "email": "user@example.com",
  "password": "securepass123",
  "username": "johndoe",
  "firstName": "John",
  "lastName": "Doe"
}
```

Response (201):

```json
{
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "johndoe",
    "firstName": "John",
    "lastName": "Doe",
    "role": "customer"
  },
  "accessToken": "eyJhbGci...",
  "refreshToken": "eyJhbGci..."
}
```

### Example: POST /api/auth/login

Request body:

```json
{
  "email": "user@example.com",
  "password": "securepass123"
}
```

Response (200):

```json
{
  "message": "Login successful",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "johndoe",
    "firstName": "John",
    "lastName": "Doe",
    "role": "customer"
  },
  "accessToken": "eyJhbGci...",
  "refreshToken": "eyJhbGci..."
}
```

### Example: POST /api/auth/refresh

Send header: `Authorization: Bearer <refresh_token>`.

Response (200):

```json
{
  "accessToken": "eyJhbGci..."
}
```

### Example: GET /api/auth/me

Response (200):

```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "johndoe",
  "firstName": "John",
  "lastName": "Doe",
  "role": "customer"
}
```

### Example: PUT /api/auth/me

Request body (all optional): `firstName`, `lastName`, `username`.

Response (200):

```json
{
  "message": "User updated successfully",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "johndoe",
    "firstName": "John",
    "lastName": "Doe",
    "role": "customer"
  }
}
```

### Example: POST /api/auth/change-password

Request body:

```json
{
  "currentPassword": "oldpass",
  "newPassword": "newpass"
}
```

Response (200):

```json
{
  "message": "Password changed successfully"
}
```

---

## Reviews

| Route | Method | Description |
|-------|--------|-------------|
| `/api/reviews` | GET | List reviews with optional filters (book_id, user_id, pagination). |
| `/api/reviews/<id>` | GET | Single review by ID. |
| `/api/reviews` | POST | Create a review (JWT required; one per user per book). |
| `/api/reviews/<id>` | PUT | Update review (JWT required, owner only). |
| `/api/reviews/<id>` | DELETE | Delete review (JWT required, owner only). |
| `/api/reviews/book/<id>` | GET | All reviews for a book with pagination. |

### Example: GET /api/reviews

Query: `page`, `per_page`, `book_id`, `user_id`.

```json
{
  "reviews": [
    {
      "id": 1,
      "book_id": 1,
      "user_id": 1,
      "rating": 4.5,
      "comment": "Great read.",
      "created_at": "2024-01-15T12:00:00"
    }
  ],
  "total": 25,
  "pages": 2,
  "currentPage": 1
}
```

### Example: GET /api/reviews/<id>

```json
{
  "id": 1,
  "book_id": 1,
  "user_id": 1,
  "rating": 4.5,
  "comment": "Great read.",
  "created_at": "2024-01-15T12:00:00",
  "book": { "id": 1, "title": "Example Book", "author": "..." }
}
```

### Example: POST /api/reviews

Request body:

```json
{
  "bookId": 1,
  "rating": 4.5,
  "text": "Great read!"
}
```

Response (201):

```json
{
  "message": "Review created successfully",
  "review": {
    "id": 1,
    "book_id": 1,
    "user_id": 1,
    "rating": 4.5,
    "comment": "Great read!",
    "created_at": "2024-01-15T12:00:00"
  }
}
```

### Example: PUT /api/reviews/<id>

Request body (optional): `rating`, `text` or `comment`.

Response (200):

```json
{
  "message": "Review updated successfully",
  "review": {
    "id": 1,
    "book_id": 1,
    "user_id": 1,
    "rating": 5,
    "comment": "Updated comment.",
    "created_at": "2024-01-15T12:00:00"
  }
}
```

### Example: DELETE /api/reviews/<id>

Response (200):

```json
{
  "message": "Review deleted successfully"
}
```

### Example: GET /api/reviews/book/<id>

Query: `page`, `per_page`.

```json
{
  "bookId": "1",
  "reviews": [
    {
      "id": 1,
      "book_id": 1,
      "user_id": 1,
      "rating": 4.5,
      "comment": "Great read.",
      "created_at": "2024-01-15T12:00:00"
    }
  ],
  "total": 12,
  "pages": 2,
  "currentPage": 1,
  "averageRating": 4.5,
  "reviewCount": 12
}
```

---

## Orders

| Route | Method | Description |
|-------|--------|-------------|
| `/api/orders` | GET | Current user's order history (JWT required). |
| `/api/orders/<id>` | GET | Single order (JWT required, owner only). |
| `/api/orders/checkout` | POST | Create order from cart (JWT required). |
| `/api/orders/<id>/pay` | POST | Mark order as paid (JWT required, owner only). |
| `/api/orders/<id>/cancel` | POST | Cancel pending order (JWT required, owner only). |
| `/api/orders/cart/validate` | POST | Validate cart (stock, prices); no auth. |
| `/api/orders/stripe/config` | GET | Stripe publishable key. |
| `/api/orders/stripe/create-intent` | POST | Create Stripe Payment Intent (JWT required). |
| `/api/orders/stripe/confirm` | POST | Confirm payment and create order (JWT required). |
| `/api/orders/stripe/webhook` | POST | Stripe webhook (signature verified when secret set). |

### Example: GET /api/orders

Query: `page`, `per_page`, `status`.

Response (200):

```json
{
  "orders": [
    {
      "id": 1,
      "user_id": 1,
      "total_amount": 49.99,
      "currency": "USD",
      "status": "Paid",
      "created_at": "2024-01-20T14:00:00"
    }
  ],
  "total": 5,
  "pages": 1,
  "currentPage": 1
}
```

### Example: GET /api/orders/<id>

Response (200):

```json
{
  "id": 1,
  "user_id": 1,
  "total_amount": 49.99,
  "currency": "USD",
  "status": "Paid",
  "created_at": "2024-01-20T14:00:00",
  "items": [
    {
      "id": 1,
      "order_id": 1,
      "book_id": 1,
      "quantity": 2,
      "unit_price": 19.99,
      "book": { "id": 1, "title": "Example Book", "author": "..." }
    }
  ]
}
```

### Example: POST /api/orders/checkout

Request body:

```json
{
  "items": [
    { "bookId": "1", "quantity": 2 },
    { "bookId": "2", "quantity": 1 }
  ]
}
```

Response (201):

```json
{
  "message": "Order created successfully",
  "order": {
    "id": 1,
    "user_id": 1,
    "total_amount": 49.99,
    "currency": "USD",
    "status": "Pending",
    "created_at": "2024-01-20T14:00:00",
    "items": [...]
  }
}
```

### Example: POST /api/orders/cart/validate

Request body:

```json
{
  "items": [
    { "bookId": "1", "quantity": 2 },
    { "bookId": "2", "quantity": 1 }
  ]
}
```

Response (200):

```json
{
  "valid": true,
  "items": [
    {
      "bookId": "1",
      "book": { "id": 1, "title": "...", "price": "19.99", ... },
      "quantity": 2,
      "unitPrice": 19.99,
      "subtotal": 39.98,
      "available": 10,
      "valid": true
    }
  ],
  "subtotal": 49.97,
  "tax": 4.0,
  "total": 53.97,
  "errors": null
}
```

### Example: GET /api/orders/stripe/config

Response (200):

```json
{
  "publishableKey": "pk_test_..."
}
```

### Example: POST /api/orders/stripe/create-intent

Request body: `items`, `customerEmail`, `customerName`, `shippingAddress` (line1, city, state, postalCode, country, etc.).

Response (200):

```json
{
  "clientSecret": "pi_xxx_secret_xxx",
  "paymentIntentId": "pi_xxx",
  "amount": 53.97,
  "currency": "usd"
}
```

### Example: POST /api/orders/stripe/confirm

Request body: `paymentIntentId`, `items`, `customerEmail`, `customerName`, `shippingAddress`.

Response (201):

```json
{
  "message": "Order created and payment confirmed successfully",
  "order": {
    "id": 1,
    "user_id": 1,
    "total_amount": 53.97,
    "currency": "USD",
    "status": "Paid",
    "stripe_payment_intent_id": "pi_xxx",
    "created_at": "2024-01-20T14:00:00",
    "items": [...]
  }
}
```

---

## Recommendations

| Route | Method | Description |
|-------|--------|-------------|
| `/api/recommendations` | GET | General recommendations (popularity-based). |
| `/api/recommendations/personalized` | GET | Personalized recommendations (JWT required). |
| `/api/recommendations/similar/<id>` | GET | Books similar to a given book. |
| `/api/recommendations/search-based` | GET | Recommendations based on search query. |

### Example: GET /api/recommendations

Query: `limit`, `exclude` (list of book IDs).

```json
{
  "recommendations": [
    { "id": 1, "title": "...", "author": "...", "price": "19.99", "genre": "Fiction", "average_rating": 4.5, "review_count": 10, "stock_quantity": 5, "popularity_score": 100, "category_id": 1, "description": "...", "isbn_13": "...", "created_at": "..." }
  ],
  "algorithm": "popularity",
  "personalized": false
}
```

### Example: GET /api/recommendations/personalized

Query: `limit`.

Response (200):

```json
{
  "recommendations": [
    { "id": 2, "title": "...", "author": "...", "price": "14.99", "genre": "Fiction", "average_rating": 4.2, "review_count": 8, "stock_quantity": 3, "popularity_score": 80, "category_id": 1, "description": "...", "isbn_13": "...", "created_at": "..." }
  ],
  "algorithm": "collaborative_heuristic",
  "personalized": true,
  "basedOn": {
    "genres": ["Fiction"],
    "categoryIds": [1]
  }
}
```

### Example: GET /api/recommendations/similar/<id>

Query: `limit`.

```json
{
  "book": {
    "id": 1,
    "title": "Example Book",
    "author": "...",
    "genre": "Fiction",
    "category_id": 1,
    "price": "19.99",
    "average_rating": 4.5,
    "stock_quantity": 10,
    "popularity_score": 100,
    "review_count": 12,
    "description": "...",
    "isbn_13": "...",
    "created_at": "..."
  },
  "similar": [
    { "id": 2, "title": "...", "author": "...", "price": "14.99", "genre": "Fiction", "average_rating": 4.2, "review_count": 8, "stock_quantity": 3, "popularity_score": 80, "category_id": 1, "description": "...", "isbn_13": "...", "created_at": "..." }
  ],
  "algorithm": "content_heuristic"
}
```

### Example: GET /api/recommendations/search-based

Query: `q`, `limit`, `exclude`.

```json
{
  "recommendations": [
    { "id": 3, "title": "...", "author": "...", "price": "12.99", "genre": "Mystery", "average_rating": 4.0, "review_count": 5, "stock_quantity": 7, "popularity_score": 60, "category_id": 2, "description": "...", "isbn_13": "...", "created_at": "..." }
  ],
  "algorithm": "search_context",
  "query": "mystery"
}
```

---

## Error responses

- **400 Bad Request**: `{ "error": "description" }`
- **401 Unauthorized**: Missing or invalid JWT
- **403 Forbidden**: Not allowed (e.g. wrong user, missing API key when required)
- **404 Not Found**: `{ "error": "Resource not found" }` or similar
- **409 Conflict**: e.g. email/username already taken, already reviewed
- **429 Too Many Requests**: Rate limit exceeded (e.g. on login/register)
