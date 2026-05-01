/**
 * ManagerBooksPage Component
 * =========================
 * 
 * Purpose:
 *   Provides CRUD interface for managers to manage book inventory.
 *   Allows creating, editing, and deleting books.
 * 
 * Features:
 *   - List all books with pagination
 *   - Create new books
 *   - Edit existing books
 *   - Delete books
 *   - Search and filter books
 * 
 * Access:
 *   Only accessible to users with 'manager' role
 */
import { FC, useState, useEffect, type FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import NavBar from '../NavBar/NavBar';
import Footer from '../Footer/Footer';
import { booksApi, categoriesApi, ApiError } from '../../services/api';
import { logger } from '../../services/logger';
import type { Book, User, Category } from '../../services/types';
import './ManagerBooksPage.css';

interface ManagerBooksPageProps {
  isLoggedIn?: boolean;
  user?: User | null;
  userAvatar?: string | null;
  onLogout?: () => void;
  cartItemCount?: number;
}

interface BookFormData {
  title: string;
  author: string;
  isbn13: string;
  publisher: string;
  publicationDate: string;
  language: string;
  genre: string;
  description: string;
  pageCount: string;
  price: string;
  currency: string;
  stockQuantity: string;
  coverImageUrl: string;
  categoryId: string;
}

const ManagerBooksPage: FC<ManagerBooksPageProps> = ({
  isLoggedIn = false,
  user = null,
  userAvatar = null,
  onLogout,
  cartItemCount = 0,
}) => {
  const navigate = useNavigate();
  const [books, setBooks] = useState<Book[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [editingBook, setEditingBook] = useState<Book | null>(null);
  const [formData, setFormData] = useState<BookFormData>({
    title: '',
    author: '',
    isbn13: '',
    publisher: '',
    publicationDate: '',
    language: 'en',
    genre: '',
    description: '',
    pageCount: '',
    price: '',
    currency: 'USD',
    stockQuantity: '',
    coverImageUrl: '',
    categoryId: '',
  });
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  useEffect(() => {
    if (!isLoggedIn) {
      navigate('/login?redirect=' + encodeURIComponent('/manage/books'));
      return;
    }

    const canManageBooks = user?.role === 'manager' || user?.role === 'admin';
    if (!canManageBooks) {
      navigate('/');
      return;
    }

    fetchBooks();
    fetchCategories();
  }, [isLoggedIn, user, navigate, page]);

  const fetchBooks = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await booksApi.getAll({ page, perPage: 20 });
      setBooks(response.books);
      setTotalPages(response.pages);
      logger.application.info('Books loaded for manager', { count: response.books.length });
    } catch (err) {
      logger.error.log(err, { component: 'ManagerBooksPage' });
      if (err instanceof ApiError) {
        if (err.status === 403) {
          setError('Manager or admin access required');
          navigate('/');
        } else {
          setError(err.message || 'Failed to load books');
        }
      } else {
        setError('An unexpected error occurred');
      }
    } finally {
      setLoading(false);
    }
  };

  const fetchCategories = async () => {
    try {
      const cats = await categoriesApi.getAll({ rootOnly: true });
      setCategories(cats);
    } catch (err) {
      logger.error.log(err, { component: 'ManagerBooksPage' });
    }
  };

  const handleCreate = () => {
    setEditingBook(null);
    setFormData({
      title: '',
      author: '',
      isbn13: '',
      publisher: '',
      publicationDate: '',
      language: 'en',
      genre: '',
      description: '',
      pageCount: '',
      price: '',
      currency: 'USD',
      stockQuantity: '',
      coverImageUrl: '',
      categoryId: '',
    });
    setShowForm(true);
  };

  const handleEdit = (book: Book) => {
    setEditingBook(book);
    setFormData({
      title: book.title,
      author: book.author,
      isbn13: book.isbn,
      publisher: book.publisher,
      publicationDate: book.publicationDate ? book.publicationDate.split('T')[0] : '',
      language: book.language,
      genre: book.genre || '',
      description: book.description || '',
      pageCount: book.pageCount?.toString() || '',
      price: book.price.toString(),
      currency: book.currency,
      stockQuantity: book.stockQuantity.toString(),
      coverImageUrl: book.imageUrl || '',
      categoryId: book.categoryId?.toString() || '',
    });
    setShowForm(true);
  };

  const handleDelete = async (bookId: string) => {
    if (!window.confirm('Are you sure you want to delete this book?')) {
      return;
    }

    try {
      await booksApi.delete(bookId);
      logger.application.info('Book deleted', { bookId });
      fetchBooks();
    } catch (err) {
      logger.error.log(err, { component: 'ManagerBooksPage' });
      if (err instanceof ApiError) {
        alert(err.message || 'Failed to delete book');
      } else {
        alert('An unexpected error occurred');
      }
    }
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();

    try {
      const bookPayload: any = {
        title: formData.title,
        author: formData.author,
        isbn13: formData.isbn13,
        price: parseFloat(formData.price),
      };

      if (formData.publisher) bookPayload.publisher = formData.publisher;
      if (formData.publicationDate) bookPayload.publicationDate = formData.publicationDate;
      if (formData.language) bookPayload.language = formData.language;
      if (formData.genre) bookPayload.genre = formData.genre;
      if (formData.description) bookPayload.description = formData.description;
      if (formData.pageCount) bookPayload.pageCount = parseInt(formData.pageCount);
      if (formData.currency) bookPayload.currency = formData.currency;
      if (formData.stockQuantity) bookPayload.stockQuantity = parseInt(formData.stockQuantity);
      if (formData.coverImageUrl) bookPayload.coverImageUrl = formData.coverImageUrl;
      if (formData.categoryId) bookPayload.categoryId = parseInt(formData.categoryId);

      if (editingBook) {
        await booksApi.update(editingBook.id, bookPayload);
        logger.application.info('Book updated', { bookId: editingBook.id });
      } else {
        await booksApi.create(bookPayload);
        logger.application.info('Book created');
      }

      setShowForm(false);
      setEditingBook(null);
      fetchBooks();
    } catch (err) {
      logger.error.log(err, { component: 'ManagerBooksPage' });
      if (err instanceof ApiError) {
        alert(err.message || 'Failed to save book');
      } else {
        alert('An unexpected error occurred');
      }
    }
  };

  const formatPrice = (price: number, currency: string = 'USD') => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency,
    }).format(price);
  };

  if (loading && books.length === 0) {
    return (
      <div className="manager-books-page">
        <NavBar
          isLoggedIn={isLoggedIn}
          user={user}
          userAvatar={userAvatar}
          onLogout={onLogout}
          cartItemCount={cartItemCount}
        />
        <main className="manager-books-main">
          <div className="loading-container">
            <div className="loading-spinner"></div>
            <p>Loading books...</p>
          </div>
        </main>
        <Footer />
      </div>
    );
  }

  return (
    <div className="manager-books-page">
      <NavBar
        isLoggedIn={isLoggedIn}
        user={user}
        userAvatar={userAvatar}
        onLogout={onLogout}
        cartItemCount={cartItemCount}
      />
      <main className="manager-books-main">
        <div className="manager-books-container">
          <div className="manager-books-header">
            <h1>Manage Books</h1>
            <button className="btn-primary" onClick={handleCreate}>
              + Add New Book
            </button>
          </div>

          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          {showForm && (
            <div className="book-form-modal">
              <div className="book-form-content">
                <div className="book-form-header">
                  <h2>{editingBook ? 'Edit Book' : 'Create New Book'}</h2>
                  <button
                    className="close-button"
                    onClick={() => {
                      setShowForm(false);
                      setEditingBook(null);
                    }}
                  >
                    ×
                  </button>
                </div>
                <form onSubmit={handleSubmit} className="book-form">
                  <div className="form-row">
                    <div className="form-group">
                      <label>Title *</label>
                      <input
                        type="text"
                        required
                        value={formData.title}
                        onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                      />
                    </div>
                    <div className="form-group">
                      <label>Author *</label>
                      <input
                        type="text"
                        required
                        value={formData.author}
                        onChange={(e) => setFormData({ ...formData, author: e.target.value })}
                      />
                    </div>
                  </div>

                  <div className="form-row">
                    <div className="form-group">
                      <label>ISBN-13 *</label>
                      <input
                        type="text"
                        required
                        value={formData.isbn13}
                        onChange={(e) => setFormData({ ...formData, isbn13: e.target.value })}
                      />
                    </div>
                    <div className="form-group">
                      <label>Price *</label>
                      <input
                        type="number"
                        step="0.01"
                        required
                        value={formData.price}
                        onChange={(e) => setFormData({ ...formData, price: e.target.value })}
                      />
                    </div>
                  </div>

                  <div className="form-row">
                    <div className="form-group">
                      <label>Publisher</label>
                      <input
                        type="text"
                        value={formData.publisher}
                        onChange={(e) => setFormData({ ...formData, publisher: e.target.value })}
                      />
                    </div>
                    <div className="form-group">
                      <label>Publication Date</label>
                      <input
                        type="date"
                        value={formData.publicationDate}
                        onChange={(e) => setFormData({ ...formData, publicationDate: e.target.value })}
                      />
                    </div>
                  </div>

                  <div className="form-row">
                    <div className="form-group">
                      <label>Genre</label>
                      <input
                        type="text"
                        value={formData.genre}
                        onChange={(e) => setFormData({ ...formData, genre: e.target.value })}
                      />
                    </div>
                    <div className="form-group">
                      <label>Language</label>
                      <input
                        type="text"
                        value={formData.language}
                        onChange={(e) => setFormData({ ...formData, language: e.target.value })}
                      />
                    </div>
                  </div>

                  <div className="form-row">
                    <div className="form-group">
                      <label>Stock Quantity</label>
                      <input
                        type="number"
                        value={formData.stockQuantity}
                        onChange={(e) => setFormData({ ...formData, stockQuantity: e.target.value })}
                      />
                    </div>
                    <div className="form-group">
                      <label>Page Count</label>
                      <input
                        type="number"
                        value={formData.pageCount}
                        onChange={(e) => setFormData({ ...formData, pageCount: e.target.value })}
                      />
                    </div>
                  </div>

                  <div className="form-group">
                    <label>Category</label>
                    <select
                      value={formData.categoryId}
                      onChange={(e) => setFormData({ ...formData, categoryId: e.target.value })}
                    >
                      <option value="">None</option>
                      {categories.map((cat) => (
                        <option key={cat.id} value={cat.id}>
                          {cat.name}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div className="form-group">
                    <label>Cover Image URL</label>
                    <input
                      type="url"
                      value={formData.coverImageUrl}
                      onChange={(e) => setFormData({ ...formData, coverImageUrl: e.target.value })}
                    />
                  </div>

                  <div className="form-group">
                    <label>Description</label>
                    <textarea
                      rows={4}
                      value={formData.description}
                      onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    />
                  </div>

                  <div className="form-actions">
                    <button type="button" className="btn-secondary" onClick={() => setShowForm(false)}>
                      Cancel
                    </button>
                    <button type="submit" className="btn-primary">
                      {editingBook ? 'Update Book' : 'Create Book'}
                    </button>
                  </div>
                </form>
              </div>
            </div>
          )}

          <div className="books-table-container">
            <table className="books-table">
              <thead>
                <tr>
                  <th>Title</th>
                  <th>Author</th>
                  <th>Price</th>
                  <th>Stock</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {books.map((book) => (
                  <tr key={book.id}>
                    <td>{book.title}</td>
                    <td>{book.author}</td>
                    <td>{formatPrice(book.price, book.currency)}</td>
                    <td>{book.stockQuantity}</td>
                    <td>
                      <button
                        className="btn-edit"
                        onClick={() => handleEdit(book)}
                      >
                        Edit
                      </button>
                      <button
                        className="btn-delete"
                        onClick={() => handleDelete(book.id)}
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {totalPages > 1 && (
              <div className="pagination">
                <button
                  disabled={page === 1}
                  onClick={() => setPage(page - 1)}
                >
                  Previous
                </button>
                <span>Page {page} of {totalPages}</span>
                <button
                  disabled={page === totalPages}
                  onClick={() => setPage(page + 1)}
                >
                  Next
                </button>
              </div>
            )}
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
};

export default ManagerBooksPage;

