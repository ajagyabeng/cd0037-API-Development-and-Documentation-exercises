import unittest
import json
from flaskr import create_app
from models import setup_db, Book

class BookshelfTestCast(unittest.TestCase):
  """This class represents the bookshelf test case"""
  
  def setUp(self):
    """Define test variables and initialize app"""
    self.app = create_app()
    self.client = self.app.test_client
    self.database_name = "bookshelf_test"
    self.database_path =  f"postgresql://postgres:0501@localhost:5432/{self.database_name}" 
    setup_db(self.app, self.database_path)
    self.new_book = {
      'title': 'Anansi Story',
      'autor': 'Kwaku Ananse',
      'rating': 5
    }

  def tearDown(self):
    """Executed after reach test"""
    pass
  
  # --------GET BOOKS---------
  def test_get_paginated_books(self):
    """test for endpoint to get books"""
    res = self.client().get('/books')
    data = json.loads(res.data)

    self.assertEqual(res.status_code, 200)
    self.assertEqual(data['success'], True)
    self.assertTrue(data['total_books'])
    self.assertTrue(len(data['books']))
  
  def test_404_sent_request_beyond_valid_page(self):
    """test for expected errors for '/books' endpoint"""
    res = self.client().get('/books?page=100')
    data = json.loads(res.data)

    self.assertEqual(res.status_code, 404)
    self.assertEqual(data['success'], False)
    self.assertEqual(data['message'], 'resource not found')

  
  # ----------UPDATE BOOK---------
  # def test_update_book_rating(self):
  #   """test for endpoint to update book"""
  #   res = self.client().get('/book/5', json={'rating': 1})
  #   data = json.loads(res.data)
  #   book = Book.query.filter(Book.id == 5).one_or_none()

  #   self.assertEqual(res.status_code, 200)
  #   self.assertEqual(data['success'], True)
  #   self.assertEqual(book.format()['rating'], 1)

# makes the test conveniently executable
if __name__ == "__main__":
  unittest.main()
