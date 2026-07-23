"""
Train recommender models from the current database.

Usage (from the api/ directory):
    python train_recommender.py
"""
import os
import sys

from App import create_app
from routes.recommendations import _collect_training_payload
from services.recommender import get_recommender_service, reset_recommender_service


def main():
    config_name = os.environ.get('FLASK_ENV', 'development')
    app = create_app(config_name)

    with app.app_context():
        model_path = app.config.get('RECOMMENDER_MODEL_PATH', 'models/recommender')
        reset_recommender_service()
        service = get_recommender_service(model_path=model_path)
        service.initialize(force_retrain=True)

        books_data, ratings_data, user_interactions = _collect_training_payload()
        if not books_data:
            print('No books found in the database. Nothing to train.')
            return 1

        service.train_all(books_data, ratings_data, user_interactions)
        print(
            f'Trained recommender on {len(books_data)} books, '
            f'{len(ratings_data)} ratings, '
            f'{len(user_interactions)} interactions.'
        )
        print(f'Models saved to: {os.path.abspath(model_path)}')
        return 0


if __name__ == '__main__':
    sys.exit(main())
