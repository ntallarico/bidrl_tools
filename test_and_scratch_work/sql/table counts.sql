SELECT
	(SELECT count(*) FROM auctions) as auctions
	, (SELECT count(*) FROM items) as items
	, (SELECT count(*) FROM bids) as bids
	, (SELECT count(*) FROM images) as images