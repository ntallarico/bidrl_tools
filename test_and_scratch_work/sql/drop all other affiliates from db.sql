-- Delete bids for items in auctions not belonging to affiliate_id '47'
DELETE FROM bids
WHERE item_id IN (
    SELECT item_id
    FROM items
    WHERE auction_id IN (
        SELECT auction_id
        FROM auctions
        WHERE affiliate_id != '47'
    )
);

-- Delete images for items in auctions not belonging to affiliate_id '47'
DELETE FROM images
WHERE item_id IN (
    SELECT item_id
    FROM items
    WHERE auction_id IN (
        SELECT auction_id
        FROM auctions
        WHERE affiliate_id != '47'
    )
);

-- Delete items in auctions not belonging to affiliate_id '47'
DELETE FROM items
WHERE auction_id IN (
    SELECT auction_id
    FROM auctions
    WHERE affiliate_id != '47'
);

DELETE FROM auctions WHERE affiliate_id != '47';

VACUUM;