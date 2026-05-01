# CuriousBooks API

The Curious Books AI Recommender System is an e-commerce web application designed to improve the online book shopping experience by delivering personalized book recommendations based on user preferences and reading behavior. Traditional online bookstores often present users with an overwhelming number of options, which can lead to decision fatigue and abandoned searches. This project addresses that challenge by defining functional and non-functional requirements for a system that guides users toward relevant book selections in an efficient and intuitive manner. The system will support core e-commerce capabilities including user authentication, browsing and searching for books, viewing detailed book information, managing a shopping cart, and completing secure checkout processes. In addition, the system defines requirements for an intelligent recommendation feature that suggests books based on content similarity and patterns of user behavior. The outcome of this requirements specification is to provide a clear, structured foundation that guides the system’s design, development, and testing phases while ensuring alignment with user needs and business goals.

# React + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Babel](https://babeljs.io/) (or [oxc](https://oxc.rs) when used in [rolldown-vite](https://vite.dev/guide/rolldown)) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the ESLint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and [`typescript-eslint`](https://typescript-eslint.io) in your project.

# Curious Books API

A Flask-based REST API backend for the Curious Books bookstore application.

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

# Stripe Configuration (required for checkout)
# Using test keys for development - get your keys from https://dashboard.stripe.com/test/apikeys
STRIPE_PUBLISHABLE_KEY=pk_test_51ShmmmKTQjdI7MuphPr7dXH7LtoHmO5LZxgYam9dJaIsgoi9DurxSo2peJ1ZGMMH9sSHdFcIxQ6OvKCRz4RPoDbs00pjQBAbfZ
STRIPE_SECRET_KEY=sk_test_51ShmmmKTQjdI7MupENFcBi5BsxFOEtA7eJxJaPfN3YP11LcjpLA9BMnCxkhxApE7pVSQF44TDAm7cNDD3lAPxnUR00RKHnDpdK
```

**Important**: Never commit your `.env` file to version control. The Stripe keys should be kept secure.

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

### Stripe Payment
- `GET /api/orders/stripe/config` - Get Stripe publishable key
- `POST /api/orders/stripe/create-intent` - Create Stripe payment intent (requires auth)
- `POST /api/orders/stripe/confirm` - Confirm payment and create order (requires auth)

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

The frontend (Curious Books) uses the API through the service layer in:
- `CuriousBooks/src/services/api.ts` - API client
- `CuriousBooks/src/services/types.ts` - TypeScript interfaces

Configure the API URL in the frontend:
```env
VITE_API_URL=http://localhost:5000/api
```

## Stripe Payment Integration

The application includes a complete Stripe checkout flow:

1. **Cart Management**: Users can update quantities for each item in the cart
2. **Checkout Page**: Collects shipping information and payment details
3. **Stripe Payment**: Uses Stripe Elements for secure card input
4. **Order Creation**: After successful payment, order is created with customer data stored in database

### Database Schema Updates

The `Order` model has been extended to store:
- Stripe payment intent ID
- Stripe customer ID
- Customer email and name
- Complete shipping address

### Setup Steps

1. Get your Stripe API keys from https://dashboard.stripe.com/apikeys
2. Add them to your `.env` file (see configuration above)
3. Install frontend dependencies: `cd CuriousBooks && npm install`
4. The checkout flow will automatically use Stripe for payment processing

**Security Note**: Stripe keys are stored in environment variables and never exposed to the frontend. Only the publishable key is sent to the client for Stripe Elements initialization.

## Development

### Running Tests
```bash
pytest
```

### Production Deployment
```bash
gunicorn App:app -w 4 -b 0.0.0.0:5000
```

