import unittest
import time

from flask_testing import LiveServerTestCase
from selenium import webdriver

from app import app


class TestBase(LiveServerTestCase):
    def create_app(self):
        return app

    def setUp(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--headless')
        options.add_argument('--window-size=1920,1080')
        self.driver = webdriver.Chrome(chrome_options=options)
        self.driver.get(self.get_server_url())

    def tearDown(self):
        self.driver.quit()


class TestInterface(TestBase):
    def test_menu(self):
        """Check menu steps are activate in order"""
        step1 = self.driver.find_element_by_id('step1')
        self.assertIn('active', step1.get_attribute('class'))

        gmap = self.driver.find_element_by_id('map_canvas')

        actions = webdriver.common.action_chains.ActionChains(self.driver)
        actions.move_to_element_with_offset(gmap,150,100)
        actions.click()
        actions.perform()

        time.sleep(1)

        step2 = self.driver.find_element_by_id('step2')
        self.assertIn('active', step2.get_attribute('class'))
        self.assertNotIn('active', step1.get_attribute('class'))

        actions = webdriver.common.action_chains.ActionChains(self.driver)
        actions.move_to_element_with_offset(gmap, 100, 100)
        actions.click()
        actions.perform()

        time.sleep(1)

        step3 = self.driver.find_element_by_id('step3')
        self.assertIn('active', step3.get_attribute('class'))
        self.assertNotIn('active', step2.get_attribute('class'))
        self.assertNotIn('active', step1.get_attribute('class'))

        reset = self.driver.find_element_by_id('reset')
        reset.click()

        time.sleep(1)

        self.assertIn('active', step1.get_attribute('class'))
        self.assertNotIn('active', step2.get_attribute('class'))
        self.assertNotIn('active', step3.get_attribute('class'))
    
    def test_deeplink(self):
        """Check that deeplinks load with results pre-built"""
        # Fujisan from Tokyo Skytree
        self.driver.get(self.driver.current_url + '/#pov=35.71,139.810744&poi=35.363976,138.732217')

        time.sleep(1)

        step1 = self.driver.find_element_by_id('step1')
        step2 = self.driver.find_element_by_id('step2')
        step3 = self.driver.find_element_by_id('step3')

        self.assertIn('active', step3.get_attribute('class'), 'Step 3 not active')
        self.assertNotIn('active', step1.get_attribute('class'), 'Step 1 active')
        self.assertNotIn('active', step2.get_attribute('class'), 'Step 2 active')

        results = self.driver.find_element_by_id('results')

        self.assertIn('Sunset', results.text)
        self.assertIn('February 02', results.text)
        self.assertIn('November 05', results.text)


if __name__ == '__main__':
    unittest.main()
