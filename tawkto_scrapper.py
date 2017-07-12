# -*- coding: utf-8 -*-
import time as system_time
import unicodecsv as csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

TAWKTO_URL = "https://dashboard.tawk.to/login"
PHANTOM_JS_PATH = "phantomjs"
TIME_FORMAT_1 = '%A, %B %d %Y, %H:%M'


class TawkToScrapper(object):

    script_to_load_all_messages = """
        function infiniteScroll(tableHeight, table, limit, count) {
            table.scrollIntoView(0, 1000);

            if(count == limit)
                return;

            setTimeout(function()
            {
                infiniteScroll(tableHeight, table, limit, count + 1);

            }, 2000);
        }
        var table = document.getElementById('conversation-list').children[0];
        var tableHeight = 0;
        infiniteScroll(tableHeight, table, 30, 1)
    """

    def __init__(self):
        self.browser = webdriver.PhantomJS(PHANTOM_JS_PATH)
        self.browser.delete_all_cookies()
        self.browser.set_window_size(1920, 1080)

    def login(self, username, password):
        username_field = self.browser.find_element_by_id("email")
        password_field = self.browser.find_element_by_id("password")
        username_field.send_keys(username)
        password_field.send_keys(password)
        login_attempt = self.browser.find_element_by_xpath("//*[@type='submit']")
        login_attempt.submit()
        self.wait_until_element_id_loaded('wid-id-0')

    def wait_until_element_id_loaded(self, element_id):
        try:
            WebDriverWait(self.browser, 120).until(EC.presence_of_element_located((By.ID, element_id)))
            print("Successfully wait for element with id {}".format(element_id))
        except TimeoutException:
            print("Wait timeout for element with id {}".format(element_id))
            self.browser.save_screenshot('error.png')

    def wait_until_element_id_hidden(self, element_id):
        try:
            WebDriverWait(self.browser, 120).until(EC.invisibility_of_element_located((By.ID, element_id)))
            print("Successfully wait for element with id{}".format(element_id))
        except TimeoutException:
            print("Wait timeout for element with id{}".format(element_id))
            self.browser.save_screenshot('error.png')

    def back_to_conversation_list_from_conversation_detail(self):
        self.wait_until_element_id_loaded('close-conversation')
        count = 0
        while (not self.browser.find_element_by_id('close-conversation').is_displayed() and
               count < 30):
            system_time.sleep(1)
            count += 1
        try:
            self.browser.find_element_by_id('close-conversation').click()
        except Exception:
            system_time.sleep(5)
            self.back_to_conversation_list_from_conversation_detail()
        self.wait_until_element_id_loaded('conversation-list')
        while (len(self.browser.find_element_by_id('conversation-list').find_elements_by_tag_name('tr')) == 0):
            system_time.sleep(1)

    def switch_to_default_list_message_menu(self):
        self.browser.get('https://dashboard.tawk.to/#/messaging')
        self.wait_until_element_id_loaded('conversations-properties')
        self.wait_until_element_id_loaded('conversation-list')
        if not self.browser.find_element_by_id('conversation-list').is_displayed():
            self.back_to_conversation_list_from_conversation_detail()
        while (len(self.browser.find_element_by_id('conversation-list').find_elements_by_tag_name('tr')) == 0):
            system_time.sleep(1)

    def load_more_messages(self):
        script_to_load_more_messages = """
            var table = document.getElementById('conversation-list').children[0];
            table.scrollIntoView(0, 1000);
        """
        self.browser.execute_script(script_to_load_more_messages)
        self.wait_until_element_id_loaded('list-loading')
        self.wait_until_element_id_hidden('list-loading')

    def load_all_messages(self):
        count = 1
        while (count < 500):
            conversation_list = self.browser.find_element_by_id('conversation-list')
            items = conversation_list.find_elements_by_tag_name('tr')
            print('{} - {}'.format(count, len(items)))
            if count == len(items):
                self.load_more_messages()
            item = conversation_list.find_elements_by_tag_name('tr')[count]
            item.click()
            print(self.get_message_transcript())
            print(self.get_conversation_detail_note())
            print(self.get_conversation_detail_details())
            print(self.get_conversation_detail_location())
            print(self.get_conversation_detail_timeline())
            print(self.get_conversation_detail_history())
            self.back_to_conversation_list_from_conversation_detail()
            count += 1

    def write_message_to_csv(self, file_path):
        with open(file_path, 'wb') as f:
            writer = csv.writer(f)
            writer.writerow(('Message',
                             'Nội dung message',
                             'Kênh liên lạc',
                             'Name',
                             'Email',
                             'Notes',
                             'Time',
                             'Tags',
                             'Location',
                             'Visitor navigated to',
                             'History'))
            count = 1
            while (count < 2000):
                conversation_list = self.browser.find_element_by_id('conversation-list')
                items = conversation_list.find_elements_by_tag_name('tr')
                print('{} - {}'.format(count, len(items)))
                try_count = 0
                while (count >= len(items) and try_count < 30):
                    self.load_more_messages()
                    system_time.sleep(1)
                    items = conversation_list.find_elements_by_tag_name('tr')
                    try_count += 1
                item = conversation_list.find_elements_by_tag_name('tr')[count]
                item.click()
                name, email, notes = self.get_conversation_detail_note()
                time, last_visit, served_by = self.get_conversation_detail_details()
                location, ip_address = self.get_conversation_detail_location()
                visited = ''
                for item in self.get_conversation_detail_timeline():
                    if 'url' in item:
                        visited += item['url'] + '\n'
                writer.writerow((
                    self.get_message_title(),
                    self.get_message_transcript(),
                    self.get_current_channel(),
                    name,
                    email,
                    notes,
                    time,
                    '',
                    location,
                    visited,
                    self.get_conversation_detail_history()
                ))
                self.back_to_conversation_list_from_conversation_detail()
                count += 1

    def get_current_channel(self):
        self.wait_until_element_id_loaded('conversations-properties')
        return self.browser.find_element_by_id('conversations-properties').find_element_by_class_name('open').find_element_by_class_name('title-section').get_attribute('innerHTML')

    def get_message_title(self):
        self.wait_until_element_id_loaded('chat-with')
        return self.browser.find_element_by_id('chat-with').get_attribute('innerHTML')

    def get_message_transcript(self):
        self.wait_until_element_id_loaded('conversations-messages-container')
        message_container = self.browser.find_element_by_id('conversations-messages-container')
        return message_container.text

    def wait_for_conversation_details_loaded_and_get_tab_element(self, tab):
        self.wait_until_element_id_loaded('conversation-details-container')
        self.wait_until_element_id_loaded(tab)
        return self.browser.find_element_by_id(tab)

    def get_conversation_detail_note(self):
        tab = self.wait_for_conversation_details_loaded_and_get_tab_element('tab1')
        name = tab.find_element_by_class_name('note-name').get_attribute('value')
        email = tab.find_element_by_class_name('note-email').get_attribute('value')
        notes = tab.find_element_by_class_name('note-text').get_attribute('value')
        return name, email, notes

    def get_conversation_detail_details(self):
        tab = self.wait_for_conversation_details_loaded_and_get_tab_element('tab2')
        time = tab.find_elements_by_tag_name('li')[0].find_element_by_class_name('info').get_attribute('innerHTML')
        last_visit = tab.find_elements_by_tag_name('li')[1].find_element_by_class_name('info').get_attribute('innerHTML')
        # device = tab.find_elements_by_tag_name('li')[2].find_element_by_class_name('info').get_attribute('innerHTML')
        served_by = tab.find_elements_by_tag_name('li')[3].find_element_by_class_name('info').get_attribute('innerHTML') if len(tab.find_elements_by_tag_name('li')) > 3 else ''
        return time, last_visit, served_by

    def get_conversation_detail_location(self):
        tab = self.wait_for_conversation_details_loaded_and_get_tab_element('tab3')
        location = tab.find_elements_by_tag_name('li')[0].find_element_by_class_name('info').get_attribute('innerHTML')
        ip_address = tab.find_elements_by_tag_name('li')[1].find_element_by_class_name('info').get_attribute('innerHTML')
        return location, ip_address

    def get_conversation_detail_timeline(self):
        tab = self.wait_for_conversation_details_loaded_and_get_tab_element('tab5')
        timeline_items = tab.find_elements_by_tag_name('li')
        result = []
        for item in timeline_items:
            if item.find_element_by_class_name('timeline-data').get_attribute('innerHTML').startswith("Visitor navigated to"):
                result.append({
                    'time': item.find_element_by_class_name('label').get_attribute('innerHTML'),
                    'data': item.find_element_by_class_name('timeline-data').get_attribute('innerHTML'),
                    'url': item.find_element_by_tag_name('a').get_attribute('href')
                })
            else:
                result.append({
                    'time': item.find_element_by_class_name('label').get_attribute('innerHTML'),
                    'data': item.find_element_by_class_name('timeline-data').get_attribute('innerHTML')
                })
        return result

    def get_conversation_detail_history(self):
        tab = self.wait_for_conversation_details_loaded_and_get_tab_element('tab4')
        try:
            tab.find_elements_by_tag_name('h3')
            return 'No Message'
        except Exception:
            result = []
            for item in tab.find_elements_by_tag_name('tr'):
                infos = item.find_elements_by_tag_name('td')
                result.append({
                    'name': infos[0].get_attribute('innerHTML'),
                    'time': infos[1].get_attribute('innerHTML'),
                    'number': infos[2].get_attribute('innerHTML')
                })
            return result


if __name__ == '__main__':
    try:
        scrapper = TawkToScrapper()
        scrapper.browser.get(TAWKTO_URL)
        scrapper.login('xander.analytics@gmail.com', 'xander2017')
        scrapper.switch_to_default_list_message_menu()
        # scrapper.load_all_messages()
        scrapper.write_message_to_csv('exported.csv')
    except Exception as e:
        import traceback; traceback.print_exc();
        scrapper.browser.save_screenshot('error.png')
    finally:
        scrapper.browser.close()
