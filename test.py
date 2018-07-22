from flask_testing import LiveServerTestCase
from urllib.request import urlopen
from selenium import webdriver
# Selenium requires drivers to be downloaded manually.
# For Firefox, the geckodriver which can be found here:
# https://github.com/mozilla/geckodriver/releases/
# Note that the version of the driver must be compatible
# with the installed version of Firefox
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

    def test_has_bootstrap(self):
        driver = webdriver.Firefox()
        driver.get(self.get_server_url())

        # Check if <link ...bootstrap...> found
        css = driver.find_element_by_xpath('/html/head/link')
        self.assertIn('bootstrap', css.get_attribute('href'))

        # Check that JS for bootstrap, jquery and popper are loaded
        look_for = ['bootstrap' , 'jquery', 'popper']
        scripts = driver.find_elements_by_xpath('/html/body/script')
        for s in scripts:
            src = s.get_attribute('src')
            print(src)
            for tag in look_for:
                print(tag, look_for)
                if tag in src:
                    look_for.remove(tag)
                    break
        self.assertListEqual(look_for, [])

        driver.close()


if __name__ == '__main__':
    unittest.main()
