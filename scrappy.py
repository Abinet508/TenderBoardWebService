import re
import time
import pandas as pd
import requests
from requests_html import HTML
from multiprocessing import Pool
import sqlite3

class SCRAPY_PUBLIC_PAGE:
    """
    This class is used to scrape the public tender page from the website tenderboard.gov.bh
    """
    def __init__(self) -> None:
        """
        This function is used to initialize the class variables and headers
        
        Returns:
            None
        """
        self.url = "https://www.tenderboard.gov.bh/Tenders/Public%20Tenders/"
        self.base_url = "https://www.tenderboard.gov.bh"
        self.headers = self.get_headers()
        self.ministries = self.get_all_ministries()
        
    def get_headers(self): 
        """
        This function is used to get the headers for the request

        Returns:
            dict: headers
        """
        headers = {
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-language': 'en-US,en;q=0.8',
            'content-type': 'application/json; charset=UTF-8',
            'origin': 'https://www.tenderboard.gov.bh',
            'priority': 'u=1, i',
            'referer': 'https://www.tenderboard.gov.bh/Tenders/Public%20Tenders/',
            'sec-ch-ua': '"Chromium";v="124", "Brave";v="124", "Not-A.Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'sec-gpc': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
        }
        return headers
    
    def progress_bar(self, iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
            """
            This function is used to display the progress bar

            Args:
                iteration (int): iteration number
                total (int): total number
                prefix (str): prefix string
                suffix (str): suffix string
                decimals (int): number of decimals
                length (int): length of the progress bar
                fill (str): fill character
                printEnd (str): print end character

            Returns:
                None
            """
            
            fill = '\033[92m█\033[0m'
            percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
            filledLength = int(length * iteration // total)
            bar = fill * filledLength + '-' * (length - filledLength)
            print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
            if iteration == total: 
                print(flush=True)
    
    def get_all_ministries(self):
        """
        This function is used to get all the ministries from the website

        Returns:
            list: list of dictionaries
        """
        response = requests.get(self.url,stream=True)
        content = response.content
        for chunk in response.iter_content(chunk_size=1024):
            content += chunk
        html = HTML(html=content)
        select = html.find('select#cphBaseBody_CphInnerBody_ddlMinistry')[0]
        options = select.find('option')
        ministries = []
        for option in options:
            if option.attrs['value'] == '0':
                continue
            ministries.append({
                'name': option.text,
                'value': option.attrs['value']
            })
        return ministries
    
    def get_all_pages_count(self, prequalificationOnly='false'):
        """
        This function is used to get the number of pages from the website

        Returns:
            int: number of pages
        """
        
        data = "{'tenderNumber':'','ministry':'0','category':'0','closingDate_filter':'','publicTenderOnly':'true','prequalificationOnly':'"+prequalificationOnly+"','auctionOnly':'true','sortingType':'0','listPage':'mainList', 'Page': '-1'}"
        
        # Loop until the request is successful
        while True:
            try:
                response = requests.post(
                    'https://www.tenderboard.gov.bh/Templates/TenderBoardWebService.aspx/GetCurrentPublicTenderPageCount',
                    headers=self.headers,
                    data=data,
                )
                # Check if the response is successful
                if response.status_code == 200:
                    # Return the number of pages
                    return response.json()['d']
                else:
                    continue
            except Exception as e:
                print(e)
                continue
        
    def get_general_data(self, page, prequalificationOnly='false'):
        """
        This function is used to get the data from the website

        Args:
            page (int): page number

        Returns:
            list: list of dictionaries
        """
        data = "{'tenderNumber':'','ministry':'0','category':'0','closingDate_filter':'','publicTenderOnly':'true','prequalificationOnly':'"+prequalificationOnly+"','auctionOnly':'true','sortingType':'0','listPage':'mainList', 'Page': '"+str(page)+"'}"
        success = False
        while not success:
            try:
                response = requests.post(
                    'https://www.tenderboard.gov.bh/Templates/TenderBoardWebService.aspx/GetCurrentPublicTenderByPage',
                    headers=self.headers,
                    data=data,
                )
                # Check if the response is not successful
                if response.status_code != 200: # If the response is not successful, continue
                    continue
                else: # If the response is successful, break the loop
                    success = True
            except Exception as e:
                time.sleep(1)
                continue
        try:
            # Parse the response using requests-html
            html = HTML(html=response.json()['d'])
            # Get the table and rows
            table = html.find('div.table-head')[0]
            # Get the rows from the table
            rows = html.find('div.rows')
            # Initialize the data list
            data_list = []
            
            # Iterate over the rows and columns to get the data
            for row in rows:
                # Get the columns for each row
                columns = row.find('div.column')
                
                data = {}
                # Total number of rows excluding the header
                total = len(rows) - 1
                # Iterate over the columns to get the data
                for column in columns:
                    # Skip the index column as it is not needed
                    if column.attrs['data-label'] == 'index':
                        continue
                    if column.attrs['data-label'] == 'No./Tender Subject':
                        #we need to get the tender number from the link located inside the brace then remove the tender number from the tender column text and assign it to the tender subject
                        tender_link = self.base_url + column.find('a')[0].attrs['href']
                        tender_number = column.find('span')[0].text
                        tender_subject = column.text.replace(tender_number, '').strip()
                        
                        data['Tender Subject'] = tender_subject.upper()
                        data['Tender Number'] = tender_number
                        data['Tender Link'] = tender_link
                    else:
                        data[column.attrs['data-label'].upper()] = column.text.upper()
                # Display the progress bar
                self.progress_bar(len(data_list), total, prefix = f'PAGE:{page}: PROGRESS', suffix = 'COMPLETED ', length = 50)
                # Append the data to the list
                data_list.append(data)
            return data_list
        except Exception as e:
            print(e)
            return []
        
if __name__ == '__main__':
    # Create an instance of the SCRAPY_PUBLIC_PAGE class
    scraper = SCRAPY_PUBLIC_PAGE()
    prequalification_filter = 'false'
    
    num_pages = scraper.get_all_pages_count(prequalificationOnly=prequalification_filter)
    num_pages = 100
    # Create a pool of processes to scrape the data
    with Pool(processes=50) as pool:
        # Get the data from each page
        results = pool.starmap(scraper.get_general_data, [(page, prequalification_filter) for page in range(1, num_pages + 1)])

    # Flatten the list of results
    flattened_results = [item for sublist in results for item in sublist]
    
    # Convert the results to a pandas DataFrame
    df = pd.DataFrame(flattened_results)
    
    # Save the DataFrame to a CSV file
    df.to_csv('tenderboard.csv', index=False)
    # Save the DataFrame to an Excel file
    df.to_excel('tenderboard.xlsx', index=False)
    # Save the DataFrame to a JSON file
    df.to_json('tenderboard.json', orient='records')
    # Connect to the SQLite database
    conn = sqlite3.connect('tenderboard.db')
    # Save the DataFrame to a SQLite table
    df.to_sql('tenderboard', conn, if_exists='replace', index=False)
    # Close the connection to the database
    conn.close()
    print('Data saved successfully')
  