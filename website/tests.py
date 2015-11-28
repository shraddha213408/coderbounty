from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from django.test import LiveServerTestCase
import os
os.environ['DJANGO_LIVE_TEST_SERVER_ADDRESS'] = 'localhost:8082'

from django.test.utils import override_settings
from selenium.webdriver.firefox.webdriver import WebDriver

class MySeleniumTests(LiveServerTestCase):
    fixtures = ['initial_data.json']

    @classmethod
    def setUpClass(cls):
        cls.selenium = WebDriver()
        super(MySeleniumTests, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(MySeleniumTests, cls).tearDownClass()

    @override_settings(DEBUG=True)
    def test_login(self):
        self.selenium.get('%s%s' % (self.live_server_url, '/accounts/login/'))
        username_input = self.selenium.find_element_by_name("login")
        username_input.send_keys('myuser')
        password_input = self.selenium.find_element_by_name("password")
        password_input.send_keys('secret')
        self.selenium.find_element_by_xpath('/html/body/div/div[1]/div/section/div/div/form/div/button').click()
        assert "myuser" in self.selenium.title.lower()

    @override_settings(DEBUG=True)
    def test_signup(self):
        self.selenium.get('%s%s' % (self.live_server_url, '/accounts/signup/'))
        username_input = self.selenium.find_element_by_name("username")
        username_input.send_keys('myuser2')
        username_input = self.selenium.find_element_by_name("email")
        username_input.send_keys('myuser@myuser.com')
        password_input = self.selenium.find_element_by_name("password1")
        password_input.send_keys('secret')
        password_input = self.selenium.find_element_by_name("password2")
        password_input.send_keys('secret')
        self.selenium.find_element_by_xpath('//*[@id="signup_form"]/button').click()
        assert "myuser" in self.selenium.title.lower()
