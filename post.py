import pandas as pd
import json
import logging
import requests

class DataPoster:
    def __init__(self, csv_file_path, error_log_file_path):
        self.csv_file_path = csv_file_path
        self.error_log_file_path = error_log_file_path

        # Configure logging only once
        logging.basicConfig(filename=self.error_log_file_path, level=logging.ERROR)

    def post_data(self):
        df = pd.read_csv(self.csv_file_path)

        for index, row in df.iterrows():
            part_number = row['meta:partnumber']

            if part_number:
                print(f"{index}: Posting data for part number: {part_number}")
                post_url = 'https://test.encompass.com/restfulservice/search'
                payload = {
                    "settings": {
                        "jsonUser": "AOB",
                        "jsonPassword": "V2H7G4G78NHY4D2D",
                        "programName": ""
                    },
                    "data": {
                        "searchTerm": part_number,
                        "mode": "",
                        "limitBrand": ""
                    }
                }
                payload_json = json.dumps(payload)
                response = self.post_request(post_url, payload_json)
                self.handle_post_response(response, part_number, df, index)

        df.to_csv(self.csv_file_path, index=False)

    def post_request(self, post_url, payload_json):
        response = self.make_actual_post_request(post_url, payload_json)
        return response
    
    def make_actual_post_request(self, post_url, payload_json):
        try:
            headers = {'Content-Type': 'application/json'}
            response = requests.post(post_url, data=payload_json, headers=headers)
            response.raise_for_status() 

            return response

        except requests.exceptions.RequestException as e:
            self.log_error(f"Error in making POST request: {e}")
            print(payload_json)
            return None

    def handle_post_response(self, response, part_number, df, index):
        try:
            if response is not None:
                result = json.loads(response.text) 
                parts = result.get('data', {}).get('parts', [])

                if len(parts) > 0:
                    for part in parts:
                        r_part_number = part.get('partNumber')
                        if r_part_number == part_number:
                            base_pn = part.get('basePN')

                            if base_pn is not None:
                                df['meta:basepn'] = df['meta:basepn'].astype(object)
                                df.at[index, 'meta:basepn'] = base_pn
                            else:
                                print(f"BasePN not found for part number {part_number}. Moving to the next.")
                            
                            break
                else:
                    print(f"No parts found for part number {part_number}. Moving to the next.")        
        except Exception as e:
            print(f"An error occurred: {e}")
            self.log_error(f"An error occurred: {e}")

    def log_error(self, message):
        logging.error(message)


csv_file_path = 'C:/Users/Abdullah/Documents/Abdullah/Python/data-entry/file.csv'
error_log_file_path = 'error_log.txt'

data_poster = DataPoster(csv_file_path, error_log_file_path)
data_poster.post_data()
