DROP VIEW IF EXISTS v_reporting_user;
                   
CREATE VIEW v_reporting_user AS

SELECT
	highbidder_username
FROM items
;