/*
UPDATE items
SET total_cost = ROUND(
    ROUND(tax_rate * (current_bid * (1 + buyer_premium)), 2) + 
    ROUND(current_bid * (1 + buyer_premium), 2), 
    2
);*/