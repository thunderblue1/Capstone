import React, { FC, useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { categoriesApi } from '../../services/api';
import { logger } from '../../services/logger';
import type { Category } from '../../services/types';
import './FeaturedCategories.css';

interface FeaturedCategoriesProps {}

const FeaturedCategories: FC<FeaturedCategoriesProps> = () => {
  const [categories, setCategories] = useState<Category[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadCategories = async () => {
      try {
        const data = await categoriesApi.getAll();
        setCategories(data);
        logger.application.info('Categories loaded', { count: data.length, component: 'FeaturedCategories' });
      } catch (err) {
        logger.error.log(err instanceof Error ? err : 'Failed to load categories', {
          component: 'FeaturedCategories',
          errorCode: 'CATEGORIES_LOAD_ERROR',
        });
        // Fallback to empty array if API fails
        setCategories([]);
      } finally {
        setIsLoading(false);
      }
    };

    loadCategories();
  }, []);

  if (isLoading) {
    return (
      <section className="featured-categories" data-testid="FeaturedCategories">
        <div className="featured-categories__container">
          <div className="featured-categories__loading">Loading categories...</div>
        </div>
      </section>
    );
  }

  return (
    <section className="featured-categories" data-testid="FeaturedCategories">
      <div className="featured-categories__container">
        <div className="featured-categories__list">
          {categories.map((category) => (
            <Link
              key={category.id}
              to={`/search?category=${encodeURIComponent(category.name)}`}
              className="category-tag"
            >
              {category.name}
            </Link>
          ))}
        </div>
      </div>
    </section>
  );
};

export default FeaturedCategories;
