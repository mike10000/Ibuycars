import unittest
import json
import os
import tempfile
from app import app, init_db, get_db

class NotesTestCase(unittest.TestCase):
    def setUp(self):
        self.db_fd, app.config['DATABASE'] = tempfile.mkstemp()
        app.config['TESTING'] = True
        self.app = app.test_client()
        
        # Override get_db to use the temp database
        with app.app_context():
            import sqlite3
            def get_test_db():
                db = sqlite3.connect(app.config['DATABASE'])
                db.row_factory = sqlite3.Row
                return db
            
            # Monkey patch get_db for the test context if needed, 
            # but since app.py uses a global DATABASE constant for connection,
            # we might need to rely on the fact that we can't easily change the global DATABASE var
            # without modifying app.py structure. 
            # However, app.py uses `sqlite3.connect(DATABASE)`.
            # Let's try to patch the DATABASE variable in app module.
            import app as app_module
            app_module.DATABASE = app.config['DATABASE']
            app_module.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(app.config['DATABASE'])

    def test_empty_notes(self):
        rv = self.app.get('/api/notes')
        data = json.loads(rv.data)
        self.assertTrue(data['success'])
        self.assertEqual(len(data['notes']), 0)

    def test_create_note(self):
        rv = self.app.post('/api/notes', json={
            'url': 'http://example.com/car1',
            'title': 'Test Car',
            'price': '$10,000',
            'source': 'Test Source',
            'note': 'This is a test note'
        })
        data = json.loads(rv.data)
        self.assertTrue(data['success'])

        rv = self.app.get('/api/notes')
        data = json.loads(rv.data)
        self.assertEqual(len(data['notes']), 1)
        self.assertEqual(data['notes'][0]['title'], 'Test Car')
        self.assertEqual(data['notes'][0]['note'], 'This is a test note')

    def test_update_note(self):
        # Create
        self.app.post('/api/notes', json={
            'url': 'http://example.com/car1',
            'note': 'Original note'
        })
        
        # Update
        self.app.post('/api/notes', json={
            'url': 'http://example.com/car1',
            'note': 'Updated note'
        })
        
        rv = self.app.get('/api/notes')
        data = json.loads(rv.data)
        self.assertEqual(len(data['notes']), 1)
        self.assertEqual(data['notes'][0]['note'], 'Updated note')

    def test_delete_note(self):
        # Create
        self.app.post('/api/notes', json={
            'url': 'http://example.com/car1',
            'note': 'To delete'
        })
        
        # Get ID
        rv = self.app.get('/api/notes')
        data = json.loads(rv.data)
        note_id = data['notes'][0]['id']
        
        # Delete
        rv = self.app.delete(f'/api/notes/{note_id}')
        self.assertTrue(json.loads(rv.data)['success'])
        
        # Verify
        rv = self.app.get('/api/notes')
        data = json.loads(rv.data)
        self.assertEqual(len(data['notes']), 0)

if __name__ == '__main__':
    unittest.main()
