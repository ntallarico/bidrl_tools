DROP VIEW IF EXISTS v_reporting_user;
                   
CREATE VIEW v_reporting_user AS

WITH usernames as (
	SELECT DISTINCT
		username
	FROM bids
), bid_info as (
	SELECT
		username
		, COUNT(DISTINCT b.bid_id) AS bids_placed
		, MIN(b.time_of_bid_unix) AS earliest_bid_time_unix
		, MAX(b.time_of_bid_unix) AS latest_bid_time_unix
		, COUNT(DISTINCT b.item_id) AS items_bid_on_unix
	FROM bids b
	GROUP BY
		username
)
SELECT
	u.username
	, af.company_name
	, ROUND(SUM(i.current_bid), 2) AS total_bid
	, ROUND(SUM(i.total_cost), 2) AS total_spent
	, COUNT(DISTINCT i.item_id) AS items_bought
	, MAX(i.current_bid) AS most_expensive_purchase
	, COUNT(DISTINCT IIF(i.total_cost < 2, i.item_id, NULL)) AS purchase_count_total_cost_0_to_1_99 -- count of purchases with actual cost of >$2
	, COUNT(DISTINCT IIF(i.total_cost < 5, i.item_id, NULL)) AS purchase_count_total_cost_2_to_4_99 -- count of purchases with actual cost of >$5
	, COUNT(DISTINCT IIF(i.current_bid < 2, i.item_id, NULL)) AS purchase_count_bid_0_to_1_99 -- count of purchases with bid amount of >$2
	, COUNT(DISTINCT IIF(i.current_bid < 5, i.item_id, NULL)) AS purchase_count_bid_2_to_4_99 -- count of purchases with bid amount of >$5
	, bi.bids_placed
	, bi.earliest_bid_time_unix
	, bi.latest_bid_time_unix
	, bi.items_bid_on_unix
	--, '' AS most_bought_category
	--, '' AS most_spent_category
	--, '' AS closest_snipe
	--, '' AS longest_out_bid_that_won
FROM usernames u
	LEFT JOIN items i on i.highbidder_username = u.username -- specifically join on items where the user won
	LEFT JOIN auctions au on au.auction_id = i.auction_id
	LEFT JOIN affiliates af on af.affiliate_id = au.affiliate_id
	LEFT JOIN bid_info bi on bi.username = u.username
WHERE au.status = 'closed'
GROUP BY
	u.username
	, af.company_name
;




SELECT * FROM v_reporting_user ORDER BY items_bought desc;