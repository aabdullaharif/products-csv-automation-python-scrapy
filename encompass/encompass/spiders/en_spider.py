import scrapy
import pandas as pd
import os

class EnSpiderSpider(scrapy.Spider):
    name = "en_spider"
    allowed_domains = ["encompass.com"]
    start_urls = ["https://encompass.com/"]
    
    csv_file_path = os.path.abspath('../file.csv')

        
    def parse(self, response):
        df = pd.read_csv(self.csv_file_path)

        for index, row in df.iterrows():
            df['Short description'] = df['Short description'].astype(object)
            description = row['Short description']

            if description:
                df['meta:mfgcode'] = df['meta:mfgcode'].astype(object)
                df['meta:partnumber'] = df['meta:partnumber'].astype(object)

                partnumber = description[3:]
                mfgcode = description[0:3]
                df.at[index, 'meta:partnumber'] = partnumber
                df.at[index, 'meta:mfgcode'] = mfgcode

                if partnumber:
                    form_data = {'searchTerm': partnumber }
                    yield scrapy.FormRequest.from_response(
                        response,
                        formdata=form_data,
                        formid="searchForm",
                        callback=self.parse_search_results,
                        cb_kwargs={'part_number': partnumber, 'df': df, 'index': index}
                    )
        
        df.to_csv(self.csv_file_path, index=False)

    def parse_search_results(self, response, part_number, df, index):
        if 'search' in response.url:
            table_rows = response.css("datatable-part_wrapper tr")
            for table_row in table_rows:
                table_number = table_row.css("a > b ::text").get()
                next_page_url = table_row.css("a::attr(href)").get()
                if table_number ==  part_number:
                    yield response.follow(next_page_url, callback=self.parse_product_page, cb_kwargs={'part_number': part_number, 'df': df, 'index': index})
        else:
            yield self.parse_product_page(response, df, index)

    def parse_product_page(self, response, df, index):
        price_with_currency = response.css(".ep-price-container .price ::text").get()

        if price_with_currency:
            price = float(''.join(filter(str.isdigit, price_with_currency))) / 100.0  

            df['Regular price'] = df['Regular price'].astype(float) 
            df.at[index, 'Regular price'] = price

            df.to_csv(self.csv_file_path, index=False)


    