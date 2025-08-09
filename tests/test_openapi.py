import json
import unittest
from docassemble.webapp.app_object import app
from docassemble.webapp.db_object import db
from docassemble.webapp.users.models import UserModel, Role

class OpenAPITestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()
        # Create a test admin user for the API to return
        admin_role = Role(name='admin')
        user = UserModel(email='test@example.com', nickname='testadmin', social_id='local$testadmin', active=True, first_name='Admin', last_name='User')
        user.roles.append(admin_role)
        db.session.add(admin_role)
        db.session.add(user)
        db.session.commit()
        self.admin_user_id = user.id

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_api_spec(self):
        """Test that the OpenAPI spec is valid and contains the correct paths."""
        # Log in as an admin user to access the endpoints
        with self.app as c:
            with c.session_transaction() as sess:
                sess['user_id'] = self.admin_user_id
                sess['_fresh'] = True

            res = self.app.get('/api/spec')
            self.assertEqual(res.status_code, 200)
            spec_data = json.loads(res.data)
            self.assertIn('openapi', spec_data)
            self.assertEqual(spec_data['info']['title'], 'docassemble API')
            self.assertIn('/api/users', spec_data['paths'])
            self.assertIn('User', spec_data['components']['schemas'])
            self.assertIn('Role', spec_data['components']['schemas'])

    def test_users_api(self):
        """Test the users API endpoint returns data that conforms to the spec."""
        with self.app as c:
            with c.session_transaction() as sess:
                sess['user_id'] = self.admin_user_id
                sess['_fresh'] = True

            res = self.app.get('/api/users')
            self.assertEqual(res.status_code, 200)
            users_data = json.loads(res.data)
            self.assertIsInstance(users_data, list)
            self.assertGreater(len(users_data), 0)
            user = users_data[0]
            self.assertIn('email', user)
            self.assertIn('nickname', user)
            self.assertIn('roles', user)
            self.assertIsInstance(user['roles'], list)

if __name__ == '__main__':
    unittest.main()
