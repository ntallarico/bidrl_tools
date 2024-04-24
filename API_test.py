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


def test_get_open_auctions():
    open_auctions = bf.get_open_auctions()

    for auction in open_auctions:
        print('')
        auction.display()



def test_get_item_data():
    url = "https://www.bidrl.com/auction/high-end-auction-161-johns-rd-unit-a-south-carolina-april-21-152426/item/metal-beads-item-see-pictures-19718242/"

    item_data = bf.get_item_data(url)

    print(f"ID: {item_data['id']}")
    print(f"Auction ID: {item_data['auction_id']}")
    print(f"Bid Count: {item_data['bid_count']}")
    print(f"Title: {item_data['title']}")



def test_get_auctions_item_urls():
    item_urls = bf.get_auctions_item_urls('https://www.bidrl.com/auction/outdoor-sports-auction-161-johns-rd-unit-a-south-carolina-april-25-152770/bidgallery/')
    for url in item_urls:
        print(url)



#test_get_item_data()

#test_get_open_auctions()

#test_get_auctions_item_urls()






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




user = {'name': user_email, 'pw': user_password}


browser = bf.init_webdriver('headless')
bf.login_try_loop(browser, user)


response = browser.request('GET', 'https://www.bidrl.com/myaccount/myitems')
#print(response.text[0:60])
print(response.text)


# to do: scrape favorites
# in order to do this, I will do one of 3 things:
# 1. traditional selenium scrape, navigating through the favorites pages
# 2. use requests library and api to scrape all items from all open auctions and check if any of them have is_favorite = 1
# 3. use requests library to scrape html response on favorites page and parse out the items
# the first seems inideal and I'd like to try moving away from this method if possible
# the latter two would require getting a logged in session or something somehow
# the last seems like it could be potentially inideal as the html could change slightly
# I would rank these options in order of preference: 2, 3, 1
# I will try them in this order
# 4.24.24: I tried #2 pretty thoroughly and failed. Need to send login POST request to https://www.bidrl.com/api/ajaxlogin
# but I can't get the arguments right. 'autologin' is one, and I truly cannot figure out what it is supposed to be. also 'nopass' seems like its getting
# passed in to the password argument and that confuses me. going to try to attempt to use selenium to physically pull up the browser and log in
# in hopes that I can yoink the session or whatever, close the browser, and continue via API


'''
other api reference i've seen to explore:
- https://www.bidrl.com/api/types/auctions
- https://www.bidrl.com/api/auctions
    - used by https://www.bidrl.com/pastauctions/
    - seems to gather all past auctions (possibly up to a certain point), which is incredible
- https://www.bidrl.com/api/auctionfields
- https://www.bidrl.com/api/initdata
- https://www.bidrl.com/api/affiliatesforhomepage
- https://www.bidrl.com/api/getsession
- 
'''



# thoughts:
# it may be faster / easier / more consistent / better to scrape every item on the website
# by scraping all open auctions by id and then scraping all items from all auctions
# and then checking each one for the favorite = 1 property









# example of ItemData json returned for URL: https://www.bidrl.com/auction/high-end-auction-161-johns-rd-unit-a-south-carolina-april-21-152426/item/ledmo-solar-pendant-light-upgraded-outdoor-indoor-solar-lights-89-retail-factory-sealed-19718194/
# post_url = "https://www.bidrl.com/api/ItemData"
'''
{id: "19718194"
, auction_id: "152426"
, groupid: "0"
, bid_count: "42"
, affiliate_id: "47"
, affiliate_img: "https://www.bidrl.com/user_images2/affiliate47_t.jpg"
, allow_buyer_agent: 0
, allow_custom_bids: ""
, auc_address: "161 Johns Rd. Unit A"
, auc_city: "Greer"
, auc_country: "226"
, auc_loc_override: null
, auc_ship_from_zip: ""
, auc_state: "123"
, auc_zip: "29650"
, auction_description: "<p><span style=\"font-size: 18pt; color: #00ff00;\"><strong>161 Johns Rd. Unit A</strong></span></p>\n<p><strong>Please call or email for a prepull if you have 15 items or more. </strong></p>\n<p>Items in this auction may be overstocks or returns, new or used, perfect or broken.  We share what we know about each item in pictures, titles or descriptions but we don't always know, don't test most items, and don't accept returns, exchanges or offer refunds.  If you have not previewed an item (physically inspected it in person) and must make an assumption about that item before bidding, assume it is broken and/or incomplete unless the description states otherwise; the item is probably fine, but it is always better to be safe than sorry.</p>\n<p>Online payment with credit cards are accepted only after the credit card has been manually authorized by BIDRL.COM.  To authorize a credit card for online payment, bring the card and a matching valid photo ID to the BIDRL.COM location you are purchasing from and we will be able to help you.  Credit cards for individuals other than the account owner will not be authorized for online payment.</p>\n<p>All previews/inspections must be made in person, we do not inspect items over phone or emails. All previews are limited to 15 minutes / 5 items and must have lot numbers written out on a note paper or note on cellular phone to help make your experience faster and effective. <span style=\"text-decoration: underline;\">We do not do previews during the last half hour of the day or on Saturdays</span>. Please bid accordingly.</p>\n<p><span style=\"color: #000000;\">Please note that our location does not have a restroom or a forklift. Winning bidders are responsible for bringing people to help them lift and load large/heavy items. BidRL staff may not and often can not assist with lifting or loading large items. We will be especially cautious during COVID19 social distancing laws are in effect. Any bidder who leaves trash or recycling on our premises will have their bidding privileges removed from our location. Bidders are responsible for disposing of their trash and recycling. We do not have a dumpster on our premises and can not dispose of these items for bidders.</span></p>"
, auction_group_type: "1"
, auction_id: "152426"
, auction_id_slug: "high-end-auction-161-johns-rd-unit-a-south-carolina-april-21-152426"
, auction_title: "High End Auction - 161 Johns Rd. Unit A -South Carolina - April 21"
, bid_count: "42"
, bid_history: [
    0: {
        bid: "12.00"
        , bid_time: "Apr 21, 2024 - 7:05:25 PM"
        , buyer_number: null
        , description: "1H, 48M, 25S outbid Fredrickson_buys."
        , id: "256668346"
        , time_of_bid: "2024-04-21T23:05:25+0300"
        , time_of_bid_unix: "1713740725"
        , user_name: "1H, 48M, 25S"
        }
    , 1: {
        bid: "11.75"
        , bid_time: "Apr 21, 2024 - 7:05:25 PM"
        , buyer_number: null
        , description: "Proxy bid was placed for Fredrickson_buys in response to a bid by 1H, 48M, 25S."
        , id: "256668345"
        , time_of_bid: "2024-04-21T23:05:25+0300"
        , time_of_bid_unix: "1713740725"
        , user_name: "Fredrickson_buys"
        }
    , 2: {...}
    , 3: {...}
    ]
, bidder_on_list: false
, bidding_extended: "1"
, bidding_status: "Closed"
, blind_bidding: "0"
, buy_now: "0.00"
, buyer_number: ""
, buyer_premium: "13.000"
, category_id: "336"
, category_name: "High End/Electronics"
, completed: "0"
, consignor: ""
, convenience_fee: "0"
, current_bid: "12.00"
, current_increment: "0.25"
, current_time: 1713788057
, disclaimers: "<p><strong>All items are sold \"as-is\" and \"where-is\" with no warranties expressed or implied.  BIDRL.COM does its best to provide bidders with complete and accurate information about each item, but there may be condition issues about which BIDRL.COM is unaware.  The responsibility for determining any item’s complete condition lies solely with the bidder.  Previewing prior to bidding is always recommended.</strong></p>\n<p><strong>Bidders failing to pay for items won by the payment deadline will be charged a re-listing fee calculated as 15% of their winning bid amount plus auction premium and applicable taxes.</strong></p>\n<p><strong>Bidders failing to remove items won by the removal deadline forfeit all rights to, and all monies paid for, those items.  No refunds or exchanges are given for items thus abandoned. </strong></p>\n<p style=\"font-weight: 400;\"><strong>All invoices must be paid for by the end of the 5<sup>th</sup> day after the auction close date; and picked up by the end of the 10<sup>th</sup> day. BidRL South Carolina is CLOSED Sundays - Wednesday. If the 10<sup>th</sup> day (for pickup) falls within that time, you must pick up your item before then. </strong></p>\n<p><strong>This auction has a SOFT CLOSE, meaning that any new bids placed on an item within in the last two minutes of that items scheduled closing time will extended bidding on that item by two minutes.  No unit will close for bidding until the scheduled close time has passed AND there has been no new bidding for two full minutes</strong></p>\n<p><strong>By bidding in this auction, you signify that you have read and agree to all terms, conditions and disclaimers associated with this auction.</strong></p>\n<p><strong>Bidders who have had their accounts disabled can contact us at southcarolina@bidrl.com.</strong></p>"
, discount: "0.00"
, display_consignor_name: "0"
, display_make_offer: "0"
, documents: []
, enable_shipment_quote: false
, end_date: "04/21/2024"
, end_time: "1713744445"
, end_time_display: "Sun, Apr 21, 2024 at 07:07:25 pm  ET"
, end_time_unix: "1713744445"
, ends: "1713742260"
, extend_interval: "-2"
, extend_threshold: "2"
, extended_bidding: "1"
, extra_info: ""
, fields: []
, first_to_reserve: "0"
, flat_increment: "0.25"
, google_videos: ""
, group_id: "0"
, groupid: "0"
, has_reserve: false
, has_whitelist: "0"
, hide_address: true
, hide_bidhistory_after_sale: "0"
, high_bidder: "64390"
, highbidder_username: "1H, 48M, 25S"
, id: "19718194"
, images: [
    0: {
        archived: "0"
        , image_height: "320"
        , image_url: "https://d3ugkdpeq35ojy.cloudfront.net/auctionimages/152426/1713193940/w661d43d7ec802.jpg"
        , image_width: "320"
        , thumb_url: "https://d3ugkdpeq35ojy.cloudfront.net/auctionimages/152426/1713193940/w661d43d7ec802_t.jpg"
    }
    , 1: {
        archived: "0"
        , image_height: "320"
        , image_url: "https://d3ugkdpeq35ojy.cloudfront.net/auctionimages/152426/1713193940/w661d43d70dbb5.jpg"
        , image_width: "320"
        , thumb_url: "https://d3ugkdpeq35ojy.cloudfront.net/auctionimages/152426/1713193940/w661d43d70dbb5_t.jpg"
    }
    , 2: {...}
    , 3: {...}
]
, increment: "1"
, increment_schemes_tips: {
    1: "<table class='tbl-incs'><tr><th>Low</th><th>High</th><th>Increment</th></tr><tr><td>$0.00</td><td>$100,000,000.00</td><td>$0.25</td></tr></table>"
}
, increments_array: {
    1: [{low: "0.00", high: "100000000.00", amount: "0.25"}]
    , 2: [{low: "0.00", high: "100000000.00", amount: "1.00"}]
}
, is_admin: false
, is_favorite: "0"
, is_live_online: false
, item_description: "<div class=\"accordion-content\"><div><div class=\"row\"><div class=\"column small-12 lstval\"><div class=\"ng-binding\"><div id=\"title_feature_div\" class=\"celwidget\" data-feature-name=\"title\" data-csa-c-type=\"widget\" data-csa-c-content-id=\"title\" data-csa-c-slot-id=\"title_feature_div\" data-csa-c-asin=\"B0BFRKJK9F\" data-csa-c-is-in-initial-active-row=\"false\" data-csa-c-id=\"m34j8t-83yv1v-eopia6-ckzy8a\" data-cel-widget=\"title_feature_div\"><div id=\"titleSection\" class=\"a-section a-spacing-none\"><h1 id=\"title\" class=\"a-size-large a-spacing-none\"><span id=\"productTitle\" class=\"a-size-large product-title-word-break\">LEDMO Solar Pendant Light Upgraded Outdoor Indoor Solar Lights Dimmable with Remote 3 Lighting Modes 3000K/4500K, 2x16.4ft Cable IP65 Waterproof for Shed, Barn, Gazebo, Patio</span><span id=\"titleEDPPlaceHolder\"></span></h1></div></div><div id=\"qpeTitleTag_feature_div\" class=\"celwidget\" data-feature-name=\"qpeTitleTag\" data-csa-c-type=\"widget\" data-csa-c-content-id=\"qpeTitleTag\" data-csa-c-slot-id=\"qpeTitleTag_feature_div\" data-csa-c-asin=\"B0BFRKJK9F\" data-csa-c-is-in-initial-active-row=\"false\" data-csa-c-id=\"gctv4-2vqx84-9p9oz3-y157l1\" data-cel-widget=\"qpeTitleTag_feature_div\"></div><div id=\"bylineInfo_feature_div\" class=\"celwidget\" data-feature-name=\"bylineInfo\" data-csa-c-type=\"widget\" data-csa-c-content-id=\"bylineInfo\" data-csa-c-slot-id=\"bylineInfo_feature_div\" data-csa-c-asin=\"B0BFRKJK9F\" data-csa-c-is-in-initial-active-row=\"false\" data-csa-c-id=\"jm0lrx-57blb6-iec6y6-sgt579\" data-cel-widget=\"bylineInfo_feature_div\"></div></div></div></div></div></div>"
, item_price: "0.000"
, live: "1"
, live_online: false
, liveonline_mode: "Normal"
, lot_number: "SB9027"
, mapping_address: "161 Johns Rd. Unit A"
, mapping_city: "Greer"
, mapping_country: "United States"
, mapping_state: "South Carolina"
, mapping_zip: "29650"
, minimum_bid: "12.25"
, mobile_extra_info: ""
, next: {
    rel: "next"
    , href: "/auction/high-end-auction-161-johns-rd-unit-a-south-carolina-april-21-152426/item/ledmo-solar-pendant-light-upgraded-outdoor-indoor-solar-lights-89-retail-factory-sealed-19725639/"
    , name: "LEDMO Solar Pendant Light Upgraded Outdoor Indoor Solar Lights $89 retail Factory Sealed"
    , rel: "next"
}
, next_name: "NEXT ITEM"
, payment_happens: "<p><strong><u>Full payment for all items must be received within 5 days of the auction closing date, this includes Weekends and Holidays.</u></strong><strong> This payment deadline is firm.</strong> All items not paid for by the payment deadline will be considered abandoned, the winning bidders claim to those items will be forfeited and a 15% relisting fee will be charged.</p>\n<p>Verbal or phone requests for extensions are not accepted. Failure to pay, or abuse of the extension policy, are grounds for terminating a bidders account.</p>\n<p>Online payment with credit cards are accepted only after the credit card has been manually authorized by BIDRL.COM.  To authorize a credit card for online payment, bring the card and a matching valid photo ID to the BIDRL.COM location you are purchasing from and we will be able to help you.  Credit cards for individuals other than the account owner will not be authorized for online payment.</p>"
, pre_deposit_amount: 0
, prev: {
    rel: "prev"
    , href: "/auction/high-end-auction-161-johns-rd-unit-a-south-carolina-april-21-152426/item/lokass-foldable-packable-backpack-19718193/"
    , name: "Lokass Foldable Packable Backpack "
    , rel: "prev"
}
, prev_name: "PREVIOUS ITEM"
, proxy_bid: 0
, quantity: "1"
, removal_happens: "<p><strong><u>All items must be removed from their auction location within 10 days of the auction closing date.</u></strong><strong> This removal deadline is firm.</strong><strong>  All items not removed by the removal deadline will be considered abandoned, the winning bidders claim to those items will be forfeited and any payments made will </strong><strong><u>NOT</u></strong><strong> be refunded.</strong></p>\n<p>Verbal or phone requests for extensions are not accepted. Failure to remove items, or abuse of the extension policy, are grounds for blacklisting a bidders account.</p>\n<p>Please note: If a winning bidder can not physically move or lift their own item(s) without assistance they are responsible for bringing other people to help them. There should be no expectation that BidRL staff will be able to assist with lifting or loading any bidders item(s) into their vehicle. We will help whenever we can, but please expect to bring enough people to help lift large furniture pieces or other heavy items item in case there are not enough physically capable BidRL staff to help. In some cases, bidders will be required to sign a waiver before asking BidRL for assistance loading items. The responsibility of securing items in or on vehicles lies solely on the buyer.</p>"
, reserve_met: false
, reserve_option: "standard"
, seller: "0"
, shipping_from_zip: "29650"
, show_bid_history: true
, show_terms: false
, social_sharing_title: "LEDMO%20Solar%20Pendant%20Light%20Upgraded%20Outdoor%20Indoor%20Solar%20Lights%20%2489%20retail%20Factory%20Sealed"
, start_time: "1712972820"
, start_time_display: "Fri, Apr 12, 2024 at 08:47:00 pm  ET"
, start_time_unix: "1712972820"
, starting_bid: "1.00"
, state_abbreviation: "SC "
, tax: "6.000"
, tax_rate: "6.000"
, taxable: "1"
, time_offset: 3600
, timezone: "America/New_York"
, title: "LEDMO Solar Pendant Light Upgraded Outdoor Indoor Solar Lights $89 retail Factory Sealed"
, url: "https://www.bidrl.com/auction/152426/item/ledmo-solar-pendant-light-upgraded-outdoor-indoor-solar-lights-89-retail-factory-sealed-19718194/"
, user_files_access: false
, user_has_bid: 0
, user_ship_zip: ""
, viewed: "22"
, weight: ""}
'''



'''
surveillance project

- I'll need a list of all auction ids
    - brute force?? need to be careful not to DDOS lol
- then from each auction id I'll need a list of all item ids in those auctions
    - possibly an API call for this? like a GetItems or something
- then I'll just need to loop through all auctions, then all items under each auction, then I'll have all the data! easy as that
'''