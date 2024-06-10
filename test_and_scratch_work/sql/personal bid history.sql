select * from items where highbidder_username = '1H, 48M, 25S' and bidding_status = 'Closed'

select * from items where highbidder_username = 'ndt' and bidding_status = 'Closed'

select * from items where highbidder_username = 'ndt' and bidding_status = 'Closed' and is_favorite = 0

-- show me items I bid on, showing the maximum I ended up bidding on that item, who actually won it, and how much they paid for it
select i.item_id, i.auction_id, i.description, max(b.bid), i.highbidder_username, i.current_bid
from items i
inner join bids b on b.item_id = i.item_id
where b.username = 'ndt'  and bidding_status = 'Closed'
group by i.item_id, i.auction_id, i.description, i.highbidder_username, i.current_bid
order by i.highbidder_username