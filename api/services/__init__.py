"""
Services for CuriousBooks API
"""
from .recommender import RecommenderService, get_recommender_service, reset_recommender_service

__all__ = ['RecommenderService', 'get_recommender_service', 'reset_recommender_service']

