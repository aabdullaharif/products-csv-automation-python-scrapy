import pandas as pd


def start_requests():
    csv_file_path = 'C:/Users/Abdullah/Documents/Abdullah/Python/data-entry/sheet.csv'
    df = pd.read_csv(csv_file_path)

    df['meta:mfgcode'] = df['meta:mfgcode'].astype('object')
    df['meta:partnumber'] = df['meta:partnumber'].astype('object')

    for index, description in enumerate(df['Short description']):
        if pd.notna(description):
            mfgcode = description[:3]
            partnumber = description[3:]


            df.at[index, 'meta:mfgcode'] = mfgcode
            df.at[index, 'meta:partnumber'] = partnumber

    df.to_csv(csv_file_path, index=False)

start_requests()



import scrapy
import pandas as pd

class EnSpiderSpider(scrapy.Spider):
    name = "en_spider"
    allowed_domains = ["encompass.com"]
    start_urls = ["https://encompass.com/"]
    csv_file_path = 'C:/Users/Abdullah/Documents/Abdullah/Python/data-entry/sheet.csv'

    def parse(self, response):
        df = pd.read_csv(self.csv_file_path)
        part_numbers = df['meta:partnumber']

        for part_number in part_numbers:
            if part_number: 
                form_data = {'searchTerm': part_number }
                yield scrapy.FormRequest.from_response(
                    response,
                    formdata=form_data,
                    formid="searchForm",
                    callback=self.parse_search_results,
                    cb_kwargs={'part_number': part_number}
                )

    def parse_search_results(self, response, part_number):
        if 'search' in response.url:  # Check if the URL contains 'search'
            table_rows = response.css("datatable-part_wrapper tr")
            for table_row in table_rows:
                table_number = table_row.css("a > b ::text").get()
                next_page_url = table_row.css("a::attr(href)").get()
                if table_number ==  part_number:
                    response.follow(next_page_url, callback=self.parse_product_page, cb_kwargs={'part_number': part_number})
        else:
            self.parse_product_page(response, part_number)

    def parse_product_page(self, response, part_number):
        yield {
            "url": response.url,
            "price": response.css(".ep-price-container .price ::text").get(),
            "part_number": part_number,
        }
