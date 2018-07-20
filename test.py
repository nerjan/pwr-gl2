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


if __name__ == '__main__':
    unittest.main()
