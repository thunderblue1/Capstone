# CuriousBooks API

A Flask-based REST API backend for the CuriousBooks bookstore application.

## Features

- **Books API**: Browse, search, and filter books
- **Categories API**: Manage book categories
- **Authentication**: JWT-based user authentication
- **Reviews**: User reviews and ratings
- **Orders/Checkout**: Shopping cart validation and order management
- **Recommendations**: Placeholder for ML-based book recommendations

## Getting Started

### Prerequisites

- Python 3.10+
- MySQL database (matching the schema provided)

### Installation

1. Create and activate a virtual environment:
```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables (create a `.env` file):
```env
FLASK_ENV=development
SECRET_KEY=your-secret-key
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your-password
DB_NAME=curiousbooks
JWT_SECRET_KEY=your-jwt-secret
CORS_ORIGINS=http://localhost:5173
```

4. Run the server:
```bash
python App.py
```

The API will be available at `http://localhost:5000`

## API Endpoints

### Health Check
- `GET /api/health` - Check API status

### Books
- `GET /api/books` - List all books (with pagination and filters)
- `GET /api/books/featured` - Get featured books
- `GET /api/books/search?q=<query>` - Search books
- `GET /api/books/<id>` - Get book details
- `GET /api/books/<id>/reviews` - Get book reviews
- `GET /api/books/genres` - Get all genres
- `GET /api/books/category/<name>` - Get books by category

### Categories
- `GET /api/categories` - List all categories
- `GET /api/categories/<id>` - Get category details
- `GET /api/categories/<id>/books` - Get books in category

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login
- `POST /api/auth/refresh` - Refresh access token
- `GET /api/auth/me` - Get current user (requires auth)
- `PUT /api/auth/me` - Update current user (requires auth)
- `POST /api/auth/change-password` - Change password (requires auth)

### Reviews
- `GET /api/reviews` - List reviews
- `GET /api/reviews/book/<id>` - Get reviews for a book
- `POST /api/reviews` - Create review (requires auth)
- `PUT /api/reviews/<id>` - Update review (requires auth)
- `DELETE /api/reviews/<id>` - Delete review (requires auth)

### Orders
- `GET /api/orders` - Get user orders (requires auth)
- `GET /api/orders/<id>` - Get order details (requires auth)
- `POST /api/orders/checkout` - Create order (requires auth)
- `POST /api/orders/<id>/pay` - Pay for order (requires auth)
- `POST /api/orders/<id>/cancel` - Cancel order (requires auth)
- `POST /api/orders/cart/validate` - Validate cart items

### Recommendations
- `GET /api/recommendations` - Get recommendations
- `GET /api/recommendations/personalized` - Get personalized recommendations (requires auth)
- `GET /api/recommendations/similar/<book_id>` - Get similar books
- `GET /api/recommendations/search-based?q=<query>` - Get search-based recommendations

## Project Structure

```
api/
├── App.py                 # Main application entry point
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── models/                # Database models
│   ├── __init__.py
│   ├── database.py
│   ├── user.py
│   ├── book.py
│   ├── category.py
│   ├── review.py
│   └── order.py
├── routes/                # API route handlers
│   ├── __init__.py
│   ├── auth.py
│   ├── books.py
│   ├── categories.py
│   ├── reviews.py
│   ├── orders.py
│   └── recommendations.py
├── services/              # Business logic services
│   ├── __init__.py
│   └── recommender.py     # ML recommender placeholder
└── models/recommender/    # ML model storage (future)
```

## Recommender System

The `services/recommender.py` file provides a framework for implementing ML-based recommendations:

- **PopularityRecommender**: Simple popularity-based (implemented)
- **ContentBasedRecommender**: TF-IDF/embeddings (placeholder)
- **CollaborativeFilteringRecommender**: Matrix factorization (placeholder)

To implement your own model:
1. Create a class inheriting from `BaseRecommender`
2. Implement `train()`, `predict()`, and `get_recommendations()` methods
3. Update `RecommenderService` to use your model

## Frontend Integration

The frontend (CuriousBooks) uses the API through the service layer in:
- `CuriousBooks/src/services/api.ts` - API client
- `CuriousBooks/src/services/types.ts` - TypeScript interfaces

Configure the API URL in the frontend:
```env
VITE_API_URL=http://localhost:5000/api
```

## Development

### Running Tests
```bash
pytest
```

### Production Deployment
```bash
gunicorn App:app -w 4 -b 0.0.0.0:5000
```

