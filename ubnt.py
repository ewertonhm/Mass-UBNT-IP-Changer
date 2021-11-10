import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import configparser
import pathlib
import inspect
import os, sys
import configs
import time
from configs import find_path, download_chromedriver
from os.path import exists


class Ubnt:
    def __init__(self, ip, port, protocol = 'https'):
        self.__DRIVER = []
        self.login = 'ubnt'
        self.senha = 'ubnt'
        self.ip = ip
        self.port = port
        self.protocol = protocol

        self.base_url = '{0}://{1}:{2}'.format(self.protocol, self.ip, self.port)
        self.index_url = self.base_url + '/index.cgi'
        self.login_url = self.base_url + '/login.cgi'
        self.network_url = self.base_url + '/network.cgi'
        self.system_url = self.base_url + '/system.cgi'
        self.start_driver()


    def start_driver(self):
        path = find_path()
        filename = path + 'chromedriver.exe'

        if not exists(filename):
            print("Chromedriver downloaded to path:" + download_chromedriver() + "chromedriver.exe")

        #print('aguarde...')
        options = selenium.webdriver.chrome.options.Options()
        options.headless = True
        options.add_argument('log-level=3')
        # options.setPageLoadStrategy(PageLoadStrategy.NONE);
        # options.add_argument("start-maximized")
        # options.add_argument("enable-automation")
        # options.add_argument("--headless")
        # options.add_argument("--no-sandbox")
        # options.add_argument("--disable-infobars")
        # options.add_argument("--disable-dev-shm-usage")
        # options.add_argument("--disable-browser-side-navigation")
        # options.add_argument("--disable-gpu")
        options.add_argument('ignore-certificate-errors')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])

        self.__DRIVER.append(selenium.webdriver.Chrome(executable_path=r"{0}".format(filename), options=options))

    def test_conn(self):
        try:
            self.__DRIVER[0].get(self.base_url)
            if self.__DRIVER[0].find_element_by_xpath('/html/body/table/tbody/tr[1]/td[2]/table/tbody/tr[3]/td[1]/label').text == 'User Name:':
                return True
            else:
                return False
        except Exception as e:
            #print(e)
            pass

    def change_defautl_password(self):
        self.__DRIVER[0].get(self.system_url)
        self.__DRIVER[0].find_element_by_xpath('//*[@id="admin_passwd_trigger"]').click()
        self.__DRIVER[0].find_element_by_xpath('//*[@id="adminname"]').clear()
        self.__DRIVER[0].find_element_by_xpath('//*[@id="adminname"]').send_keys('admin')
        self.__DRIVER[0].find_element_by_xpath('//*[@id="OldPassword"]').send_keys('ubnt')
        self.__DRIVER[0].find_element_by_xpath('//*[@id="NewPassword"]').send_keys('newpassword')
        self.__DRIVER[0].find_element_by_xpath('//*[@id="NewPassword2"]').send_keys('newpassword')

        self.__DRIVER[0].find_element_by_xpath('//*[@id="system_change"]').click()
        time.sleep(1)
        self.__DRIVER[0].find_element_by_xpath('/html/body/table/tbody/tr[3]/td/div[1]/div/table/tbody/tr/td[2]/input[2]').click()
        print('Password alterado, aguardando as configurações serem aplicadas ...')
        time.sleep(90)




    def kill_driver(self):
        self.__DRIVER[0].quit()
        self.__DRIVER[0] = None

    def do_login(self, login, psw):
        self.login = login
        self.senha = psw

        if not self.login_url == self.__DRIVER[0].current_url:
            self.__DRIVER[0].get(self.login_url)

        self.__DRIVER[0].find_element_by_name('username').send_keys(self.login)
        self.__DRIVER[0].find_element_by_name('password').send_keys(self.senha)
        self.__DRIVER[0].find_element_by_name('password').send_keys(Keys.ENTER)

        try:
            hostname = self.__DRIVER[0].find_element_by_xpath('/html/body/table/tbody/tr[2]/td[2]/input')
            if(hostname.get_attribute('value') == "Logout"):
                return True
            else:
                return False
        except Exception as e:
            #print(e)
            return False

    def get_network_configs(self):

        if not self.network_url == self.__DRIVER[0].current_url:
            self.__DRIVER[0].get(self.network_url)
            time.sleep(1)

        try:
            ip = self.__DRIVER[0].find_element_by_xpath('//*[@id="mgmtIpAddr"]').get_attribute('value')
            mask = self.__DRIVER[0].find_element_by_xpath('//*[@id="mgmtIpNetmask"]').get_attribute('value')
            gateway = self.__DRIVER[0].find_element_by_xpath('//*[@id="mgmtGateway"]').get_attribute('value')

            configs.write_to_log('IP Address: ' + ip)
            configs.write_to_log('Netmask: ' + mask)
            configs.write_to_log('Gateway IP: ' + gateway)

        except Exception as e:
            #print(e)
            pass

    def set_network_configs(self, ip, mask, gateway):
        if not self.network_url == self.__DRIVER[0].current_url:
            self.__DRIVER[0].get(self.network_url)
            time.sleep(1)

        try:
            # IP
            self.__DRIVER[0].find_element_by_xpath('//*[@id="mgmtIpAddr"]').clear()
            self.__DRIVER[0].find_element_by_xpath('//*[@id="mgmtIpAddr"]').send_keys(ip)
            # MASK
            self.__DRIVER[0].find_element_by_xpath('//*[@id="mgmtIpNetmask"]').clear()
            self.__DRIVER[0].find_element_by_xpath('//*[@id="mgmtIpNetmask"]').send_keys(mask)

            # GATEWAY
            self.__DRIVER[0].find_element_by_xpath('//*[@id="mgmtGateway"]').clear()
            self.__DRIVER[0].find_element_by_xpath('//*[@id="mgmtGateway"]').send_keys(gateway)

            # CONFIRM
            self.__DRIVER[0].find_element_by_xpath('//*[@id="change"]').click()
            try:
                if self.__DRIVER[0].find_element_by_xpath('/html/body/div[2]/div[2]/table/tbody/tr[3]/td/font/label').text == 'Default Password must be changed to apply configuration changes!':
                    self.__DRIVER[0].find_element_by_xpath('//*[@id="dlgOldPassword"]').send_keys(self.senha)
                    self.__DRIVER[0].find_element_by_xpath('//*[@id="dlgNewPassword"]').send_keys('glock9mm')
                    self.__DRIVER[0].find_element_by_xpath('//*[@id="dlgNewPassword2"]').send_keys('glock9mm')
                    self.__DRIVER[0].find_element_by_xpath('/html/body/div[2]/div[3]/div/button[2]/span').click()
            except Exception:
                pass

            self.__DRIVER[0].find_element_by_xpath('//*[@id="apply_button"]').click()


        except Exception as e:
            #print(e)
            pass