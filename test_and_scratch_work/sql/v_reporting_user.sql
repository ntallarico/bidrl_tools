DROP VIEW IF EXISTS v_reporting_user;
                   
CREATE VIEW v_reporting_user AS

WITH usernames as (
	SELECT DISTINCT
		username
	FROM bids
)
SELECT
	u.username
	, af.company_name
	, COUNT(DISTINCT i.current_bid) AS total_bid
	, COUNT(DISTINCT i.total_cost) AS total_spent
	, COUNT(DISTINCT i.item_id) AS items_bought
	, COUNT(DISTINCT b.bid_id) AS bids_placed
	, MIN(time_of_bid_unix) AS earliest_bid_time
	, MAX(time_of_bid_unix) AS latest_bid_time
	, '' AS most_bought_category
	, '' AS most_spent_category
	, '' AS closest_snipe
	, '' AS longest_out_bid_that_won
	, '' AS most_expensive_purchase
	, '' AS dollar_something_cops
	, '' AS sub_5_dollar_cops
	, '' AS items_bid_on
	--, '' AS win_rate --calculate in tableau based on items_bought/items_bid_on
	, COUNT(DISTINCT i.auction_id) AS auctions_bought_item_in
FROM usernames u
	LEFT JOIN items i on i.highbidder_username = u.username
	LEFT JOIN auctions au on au.auction_id = i.auction_id
	LEFT JOIN affiliates af on af.affiliate_id = au.affiliate_id
	LEFT JOIN bids b on b.item_id = i.item_id
WHERE au.status = 'closed'
GROUP BY
	u.username
	, af.company_name
ORDER BY items_bought desc
;




SELECT * FROM v_reporting_user;