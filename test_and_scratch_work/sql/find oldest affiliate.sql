--find the oldest affiliate
select
	af.affiliate_id
	, af.company_name
	, min(b.time_of_bid) as earliest_bid
from affiliates af
	left join auctions auc on auc.affiliate_id = af.affiliate_id
	left join items i on i.auction_id = auc.auction_id
	left join bids b on b.item_id = i.item_id
group by
	af.affiliate_id
	, af.company_name
order by earliest_bid