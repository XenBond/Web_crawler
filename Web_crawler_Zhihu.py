from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from msedge.selenium_tools import Edge, EdgeOptions
from fake_useragent import UserAgent

import tqdm
import json
import time
import re
import random

def get_driver():
    ua = UserAgent()
    userAgent = ua.random
    options = EdgeOptions()
    # no longer effective to Zhihu. But might be still effective to other websites.
    options.use_chromium = True
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_argument(f'user-agent={userAgent}')
    options.add_experimental_option('useAutomationExtension', False)

    options.add_argument('--disable-blink-features=AutomationControlled')
    driver = Edge(executable_path='msedgedriver.exe', options=options)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            })
        """
    })
    driver.execute_cdp_cmd("Network.enable", {})
    driver.execute_cdp_cmd("Network.setExtraHTTPHeaders", {"headers": {"User-Agent": "browser1"}})
    return driver

def login_cookie():
    driver = get_driver()    
    driver.set_page_load_timeout(20)
    driver.set_script_timeout(20)
    LOGIN_URL = 'https://www.zhihu.com/'
    driver.get(LOGIN_URL)
    time.sleep(5)
    input("press Enter after you login in")
    cookies = driver.get_cookies()
    jsonCookies = json.dumps(cookies)
    # cookie to login in
    with open('Login_Cookie.txt','w') as f:
        f.write(jsonCookies)
    driver.quit()

def login():    
    driver.set_page_load_timeout(20)
    driver.set_script_timeout(20)
    LOGIN_URL = 'https://www.zhihu.com/'
    driver.get(LOGIN_URL)
    input('Enter after login.')
    time.sleep(5)
    '''
    f = open('Login_Cookie.txt')
    cookies = f.read()
    jsonCookies = json.loads(cookies)
    for co in jsonCookies:
        driver.add_cookie(co)
    driver.refresh()
    time.sleep(5)
    '''
def get_res(question_url, nb_res=32):
    '''
    TO DO:
    script the content. have a counter to count the existing scripted object.
    each time we scroll down, we need to update the new articles list.
    we will only choose those with index larger than the number of scripted articles.
    That is:
    While articles:
        for i in articles[counter:]:
            script()
            counter += 1
        scrolldown()
        update(articles)
    '''
    driver.get(question_url)

    # expand all button 'read the whole article'
    more_buttons = driver.find_elements_by_class_name('ContentItem-more')
    #for button in more_buttons:
    #    button.click() 

    # find all articles.
    # hash set to store all visited articles.
    scanned = set()
    counter = 0
    found_new = True
    while counter < nb_res and found_new:
        articles = driver.find_elements_by_css_selector('.List-item')
        found_new = False
        for i, article in tqdm.tqdm(enumerate(articles)):
            hashcode = hash(article.text)
            if hashcode in scanned:
                print(i, ' in dict.')
                continue
            else:
                print('add ', i)
                found_new = True
                scanned.add(hashcode)
            
            counter += 1
            print(article.text)
            #js='window.scrollTo(0, document.body.scrollHeight)'
            
            js = '''
            let equalNum = 0;
            window.checkBottom = false;
            window.height = 0;
            window.intervalId = setInterval(()=>{
                let currentHeight = document.body.scrollHeight;
                if(currentHeight === window.height){
                    equalNum++;
                    if(equalNum === 2){
                        clearInterval(window.intervalId);
                        window.checkBottom = true;
                    }
                }else{
                    window.height = currentHeight;
                    window.scrollTo(0,window.height);
                    window.scrollTo(0,window.height-1000);
                }
            },1500)'''
            
            driver.execute_script(js)
            driver.execute_script('window.scrollTo(0, document.body.scrollHeight)')
            time.sleep(random.random() * (i % 10))
        del articles        

if __name__ == "__main__":
    question_url = 'https://www.zhihu.com/''
    # login_cookie()
    driver = get_driver()
    login()
    get_res(question_url)
