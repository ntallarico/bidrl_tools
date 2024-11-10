from django.db import models

class ItemUserInput(models.Model):
    item_id = models.CharField(max_length=255, primary_key=True)
    auction_id = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    url = models.TextField(null=True, blank=True)
    end_time_unix = models.IntegerField(null=True, blank=True)
    item_bid_group_id = models.TextField(null=True, blank=True)
    ibg_items_to_win = models.IntegerField(null=True, blank=True)
    cost_split = models.TextField(null=True, blank=True)
    max_desired_bid = models.FloatField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    items_in_bid_group = models.IntegerField(null=True, blank=True)
    items_in_bid_group_won = models.IntegerField(null=True, blank=True)

# class Affiliate(models.Model):
#     affiliate_id = models.CharField(max_length=255, primary_key=True)
#     logo = models.TextField(null=True, blank=True)
#     do_not_display_tab = models.IntegerField(null=True, blank=True)
#     company_name = models.TextField(null=True, blank=True)
#     firstname = models.TextField(null=True, blank=True)
#     lastname = models.TextField(null=True, blank=True)
#     auc_count = models.IntegerField(null=True, blank=True)

# class Auction(models.Model):
#     auction_id = models.CharField(max_length=255, primary_key=True)
#     url = models.TextField(null=True, blank=True)
#     title = models.TextField(null=True, blank=True)
#     item_count = models.IntegerField(null=True, blank=True)
#     start_datetime = models.TextField(null=True, blank=True)
#     status = models.TextField(null=True, blank=True)
#     affiliate_id = models.ForeignKey(Affiliate, on_delete=models.CASCADE, null=True, blank=True)
#     aff_company_name = models.TextField(null=True, blank=True)
#     state_abbreviation = models.TextField(null=True, blank=True)
#     city = models.TextField(null=True, blank=True)
#     zip = models.TextField(null=True, blank=True)
#     address = models.TextField(null=True, blank=True)

# class Item(models.Model):
#     item_id = models.CharField(max_length=255, primary_key=True)
#     auction_id = models.ForeignKey(Auction, on_delete=models.CASCADE, null=True, blank=True)
#     description = models.TextField(null=True, blank=True)
#     current_bid = models.FloatField(null=True, blank=True)
#     highbidder_username = models.TextField(null=True, blank=True)
#     url = models.TextField(null=True, blank=True)
#     tax_rate = models.FloatField(null=True, blank=True)
#     buyer_premium = models.FloatField(null=True, blank=True)
#     lot_number = models.TextField(null=True, blank=True)
#     bidding_status = models.TextField(null=True, blank=True)
#     end_time_unix = models.IntegerField(null=True, blank=True)
#     bid_count = models.IntegerField(null=True, blank=True)
#     viewed = models.IntegerField(null=True, blank=True)
#     is_favorite = models.IntegerField(null=True, blank=True)
#     total_cost = models.FloatField(null=True, blank=True)

# class Bid(models.Model):
#     bid_id = models.CharField(max_length=255, primary_key=True)
#     item_id = models.ForeignKey(Item, on_delete=models.CASCADE, null=True, blank=True)
#     username = models.TextField(null=True, blank=True)
#     bid = models.FloatField(null=True, blank=True)
#     bid_time = models.TextField(null=True, blank=True)
#     time_of_bid = models.TextField(null=True, blank=True)
#     time_of_bid_unix = models.IntegerField(null=True, blank=True)
#     buyer_number = models.TextField(null=True, blank=True)
#     description = models.TextField(null=True, blank=True)

# class Invoice(models.Model):
#     invoice_id = models.CharField(max_length=255, primary_key=True)
#     date = models.TextField(null=True, blank=True)
#     link = models.TextField(null=True, blank=True)
#     total_cost = models.FloatField(null=True, blank=True)
#     expense_input_form_link = models.TextField(null=True, blank=True)

# class User(models.Model):
#     username = models.CharField(max_length=255, primary_key=True)
#     user_id = models.IntegerField(null=True, blank=True)

# class Image(models.Model):
#     item_id = models.ForeignKey(Item, on_delete=models.CASCADE)
#     image_url = models.TextField()
#     image_height = models.IntegerField(null=True, blank=True)
#     image_width = models.IntegerField(null=True, blank=True)