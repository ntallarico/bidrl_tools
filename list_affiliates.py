'''
This script scrapes and displays the list of all affiliate information from bidrl.
'''

import bidrl_functions as bf
from config import home_affiliates


def list_affiliates_main():
    affiliates = bf.scrape_affiliates()
    for affiliate in affiliates:
        is_aff_in_home_affiliates = 'no'
        if affiliate.id in home_affiliates:
           is_aff_in_home_affiliates = 'YES'
        affiliate_name_segment = "Affiliate: '" + affiliate.company_name + "'"
        print(f"{affiliate_name_segment.ljust(40)} ID: {affiliate.id.ljust(8)} In home_affiliates list: {is_aff_in_home_affiliates}")


if __name__ == "__main__":
  list_affiliates_main()

