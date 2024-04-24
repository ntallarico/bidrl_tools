import sys
import os
# tell this file that the root directory is one folder level up so that it can read our files like config, bidrl_classes, etc
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import requests
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from seleniumrequests import Chrome
import json
import time
from config import user_email, user_password, google_form_link_base
from bidrl_classes import Auction, Item
import bidrl_functions as bf


'''
Attempting here to find a way to get a logged in session so that I can send and recieve requests as a logged in account.
I want to be able to scrape favorites and such for an account.


log:

4.23.24
I tried to pretty thoroughly to figure out how to login via a post request and failed.
I tried to trace the login form from the html form on bidrl.com/login (login?v=165.html), where the function doLogin() picks up the work, then though
where that function is defined in app.rev165.j, where it sends login POST request to https://www.bidrl.com/api/ajaxlogin.
It needs some parameter 'autologin' which I cannot figure out (idk what is put into it and cannot see where its defined or from where its passed in),
and also 'nopass' seems like its getting passed into the password argument and that confuses me.

4.24.24
Tried a different method that I got to work!
I am using seleniumrequests, an extension of selenium that adds the requests function from the Requests library. This allows me to run a webdriver object
that can also send get/post requests. The webdriver object handles sessions and cookies bidirectionally automatically, allowing me to log in using
selenium actions and then continue the script using that webdriver object that logged in to run get/post requests as a logged in session.


'''







'''def get_logged_in_session(user):
    session = requests.Session() # Create a session object to persist cookies

    response = session.get('https://www.bidrl.com/login') # make GET request to get the cookies
    #response = session.get('https://www.bidrl.com/api/ajaxlogin') # make GET request to get the cookies

    login_url = 'https://www.bidrl.com/api/ajaxlogin'
    payload = {
        'user_name': user['name'] #'ndt' #
        , 'password': user['pw'] #'nopass' #
        , 'autologin': 'false'
    }

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = session.post(login_url, data=payload, headers=headers)

    print(response.text)

    # Check if login was successful
    if response.ok:
        #print("Login successful")
        # Now you can make authenticated requests with the session object
        # Example: Get a page that requires login
        page_url = 'https://www.bidrl.com/myaccount/myitems'
        response = session.get(page_url)
        print(response.text[0:60])  # or process the response in other ways
        # if we get the response "<!doctype html> <html class="no-js" lang="en" ng-app="rwd">" then we've failed
        # if we get the response "<!DOCTYPE html> <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en-US" lang="en-US">" then we've succeeded
    else:
        print("Login failed")


user = {'name': user_email, 'pw': user_password}
get_logged_in_session(user)'''



'''def post_with_angular(path, params):
    driver.execute_script("""
    // Find the form by AngularJS model or any specific identifier
    var form = document.querySelector('form[ng-submit="doLogin()"]');
    
    // Set the input values directly
    form.querySelector('input[name="username"]').value = arguments[0].username;
    form.querySelector('input[name="password"]').value = arguments[0].password;
    
    // Manually trigger the AngularJS submit function
    angular.element(form).scope().$apply(function() {
        angular.element(form).scope().doLogin();
    });
    """, params)


def post(path, params):
    driver.execute_script("""
    function post(path, params, method='post') {
        const form = document.createElement('form');
        form.method = method;
        form.action = path;
        
    
        for (const key in params) {
            if (params.hasOwnProperty(key)) {
            const hiddenField = document.createElement('input');
            hiddenField.type = 'hidden';
            hiddenField.name = key;
            hiddenField.value = params[key];
    
            form.appendChild(hiddenField);
        }
        }
    
        document.body.appendChild(form);
        form.submit();
    }
    
    post(arguments[1], arguments[0]);
    """, params, path)

driver = bf.init_browser()
driver.get('https://www.bidrl.com/login')
time.sleep(5)
try: post_with_angular(path='/login', params={'username': user_email, 'password': user_password})
except: print('failed')
time.sleep(10)
input()
driver.get('https://www.bidrl.com/myaccount/myitems')
#input()

# form.ng-submit = "doLogin()";'''



'''
user = {'name': user_email, 'pw': user_password}
browser = bf.init_browser()
bf.login_try_loop(browser, user)
time.sleep(1)

session = requests.Session() # Create a session object to persist cookies
response = session.get('https://www.bidrl.com/myaccount/myitems')
print(response.text[0:60])  # or process the response in other ways

if response.ok:
    print(response.text[0:60])
    # if we get the response "<!doctype html> <html class="no-js" lang="en" ng-app="rwd">" then we've failed
    # if we get the response "<!DOCTYPE html> <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en-US" lang="en-US">" then we've succeeded
else:
    print("GET failed")'''





browser = bf.init_logged_in_webdriver(user_email, user_password, 'headless')


response = browser.request('GET', 'https://www.bidrl.com/myaccount/myitems')
print(response.text[0:15])
#print(response.text)
















