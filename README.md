# SCRAPPY.PY CODE EXPLANATION

This document provides a detailed explanation of the `scrappy.py` script, focusing on the code excerpt from lines 82 to 98. The script is designed for web scraping, specifically targeting a webpage structured with div elements representing rows and columns.

## Overview

The script contains a portion of code that is responsible for parsing HTML content to extract data from a structured format of rows and columns. It then compiles this data into a list of dictionaries, each representing a row of data with key-value pairs corresponding to column labels and their respective data.

## Detailed Breakdown

- **HTML Row Extraction**: The code begins by searching the HTML content for a div element with a class of 'rows'. This is assumed to contain all the data rows that need to be scraped.

  ```python
  rows = html.find('div.rows')
  ```

- **Data List Initialization**: A list named `data_list` is initialized

.

 This will store dictionaries where each dictionary represents a row of data extracted from the HTML.

  ```python
  data_list = []
  ```

- **Row Iteration**: The script iterates over each row found in the `rows` collection.

  ```python
  for row in rows:
  ```

- **Column Extraction**: For each row, it finds all div elements with a class of 'column', which are assumed to represent the data columns of that row.

  ```python
  columns = row.find('div.column')
  ```

- **Data Dictionary Initialization**: A dictionary named `data` is initialized to store the data of the current row, with keys being the data labels (column names) and values being the text content of each column.

- **Total Rows Calculation**: The total number of rows is calculated by subtracting one from the length of the `rows` collection. This might be intended for progress tracking or handling pagination.

  ```python
  total = len(rows) - 1
  ```

- **Column Data Extraction**: The script iterates over each column in the current row. If a column's `data-label` attribute is 'index', it skips the column. Otherwise, it adds the column's `data-label` attribute value as a key and the column's text content as a value to the `data` dictionary.

  ```python
  for column in columns:
      if column.attrs['data-label'] == 'index':
          continue
      data[column.attrs['data-label']] = column.text
  ```

- **Progress Bar Update**: After processing each row, the script updates a progress bar. This is a visual representation of the scraping progress, showing how many rows have been processed out of the total.

  ```python
  self.progress_bar(len(data_list), total, prefix = f'PAGE:{page}: PROGRESS', suffix = 'COMPLETED ', length = 50)
  ```

- **Appending Row Data**: The `data` dictionary, now filled with the current row's data, is appended to the `data_list`.

  ```python
  data_list.append(data)
  ```

- **Return Data List**: Once all rows have been processed, the `data_list` is returned. This list contains all the scraped data in a structured format.

- **Main Block**: The script's main block initializes a scraper instance and sets a variable `num_pages` to 100, presumably to control the number of pages to scrape.

  ```python
  if __name__ == '__main__':
      scraper = SCRAPY_PUBLIC_PAGE()
      num_pages = 100
  ```

## Conclusion

The provided code excerpt from `scrappy.py` demonstrates a structured approach to web scraping, where HTML content is parsed to extract data organized in rows and columns. The script efficiently compiles this data into a list of dictionaries, facilitating further processing or analysis.
```