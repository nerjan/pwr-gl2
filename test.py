from flask import Flask
from flask_testing import LiveServerTestCase
from urllib.request import urlopen
import unittest
import os
import app


class TestServer(LiveServerTestCase):

    def create_app(self):
        app.prepare_env()
        app.secret_key = os.urandom(24)
        return app.app

    def test_server_is_up_and_running(self):
        response = urlopen(self.get_server_url())
        self.assertEqual(response.code, 200)

    def test_if_environment_set(self):
        self.assertIn('GENOMELINK_CLIENT_ID', os.environ)
        self.assertIn('GENOMELINK_CLIENT_SECRET', os.environ)
        self.assertIn('GENOMELINK_CALLBACK_URL', os.environ)


if __name__ == '__main__':
    unittest.main()
