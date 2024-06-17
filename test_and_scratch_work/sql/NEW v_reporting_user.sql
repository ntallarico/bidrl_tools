WITH bid_info as (
	-- this CTE expands out from bids, creating the affiliate-auction-item-bid scaffolding needed to later join everything else onto
	-- this also takes the opportunity of accessing bid-level data to generate some bid data aggregations
	SELECT
		b.username
		, af.affiliate_id
		, au.auction_id
		, i.item_id
		, COUNT(DISTINCT b.bid_id) AS bids_placed
		, MIN(b.time_of_bid_unix) AS earliest_bid_time_unix
		, MAX(b.time_of_bid_unix) AS latest_bid_time_unix
		, COUNT(DISTINCT b.item_id) AS items_bid_on
	FROM bids b
		INNER JOIN items i ON i.item_id = b.item_id
		INNER JOIN auctions au ON au.auction_id = i.auction_id
		INNER JOIN affiliates af ON af.affiliate_id = au.affiliate_id
	GROUP BY
		b.username
		, af.affiliate_id
		, au.auction_id
		, i.item_id
)
SELECT
	bi.username
	, af.company_name
	, ROUND(SUM(i_won.current_bid), 2) AS total_bid
	, ROUND(SUM(i_won.total_cost), 2) AS total_spent
	, COUNT(DISTINCT i_won.item_id) AS items_bought
	, MAX(i_won.current_bid) AS most_expensive_purchase
	, COUNT(DISTINCT IIF(i_won.total_cost < 2, i_won.item_id, NULL)) AS purchase_count_total_cost_0_to_1_99 -- count of purchases with actual cost of >$2
	, COUNT(DISTINCT IIF(i_won.total_cost < 5, i_won.item_id, NULL)) AS purchase_count_total_cost_2_to_4_99 -- count of purchases with actual cost of >$5
	, COUNT(DISTINCT IIF(i_won.current_bid < 2, i_won.item_id, NULL)) AS purchase_count_bid_0_to_1_99 -- count of purchases with bid amount of >$2
	, COUNT(DISTINCT IIF(i_won.current_bid < 5, i_won.item_id, NULL)) AS purchase_count_bid_2_to_4_99 -- count of purchases with bid amount of >$5
	, bi.bids_placed
	, bi.earliest_bid_time_unix
	, bi.latest_bid_time_unix
	, bi.items_bid_on
	--, '' AS most_bought_category
	--, '' AS most_spent_category
	--, '' AS closest_snipe
	--, '' AS longest_out_bid_that_won
FROM bid_info bi
	INNER JOIN affiliates af on af.affiliate_id = bi.affiliate_id
	INNER JOIN auctions au on au.auction_id = bi.auction_id
	--INNER JOIN items i on i.item_id = bi.item_id
	LEFT JOIN items i_won on i_won.highbidder_username = bi.username -- specifically join on items where the user won
WHERE au.status = 'closed'
GROUP BY
	bi.username
	, af.company_name
;