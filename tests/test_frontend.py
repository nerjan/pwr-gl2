from flask_testing import LiveServerTestCase
from urllib.request import urlopen
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
# Selenium requires drivers to be downloaded manually.
# For Firefox, the geckodriver which can be found here:
# https://github.com/mozilla/geckodriver/releases/
# Note that the version of the driver must be compatible
# with the installed version of Firefox
import os
from app import create_app


class TestServer(LiveServerTestCase):

    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ENV = 'development'
    TESTING = True

    def create_app(self):
        return create_app(self)

    def test_server_is_up_and_running(self):
        response = urlopen(self.get_server_url())
        self.assertEqual(response.code, 200)

    def test_if_environment_set(self):
        self.assertIn('GENOMELINK_CLIENT_ID', os.environ)
        self.assertIn('GENOMELINK_CLIENT_SECRET', os.environ)
        self.assertIn('GENOMELINK_CALLBACK_URL', os.environ)

    def test_has_bootstrap(self):
        options = Options()
        options.headless = True
        driver = webdriver.Firefox(options=options)
        driver.get(self.get_server_url())

        # Check if <link ...bootstrap...> found
        css = driver.find_element_by_xpath('/html/head/link')
        self.assertIn('bootstrap', css.get_attribute('href'))

        # Check that JS for bootstrap, jquery and popper are loaded
        look_for = ['bootstrap' , 'jquery', 'popper']
        scripts = driver.find_elements_by_xpath('/html/body/script')
        for s in scripts:
            src = s.get_attribute('src')
            for tag in look_for:
                if tag in src:
                    look_for.remove(tag)
                    break
        self.assertListEqual(look_for, [])

        driver.quit()
