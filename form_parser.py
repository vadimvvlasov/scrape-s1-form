# import libraries
import json
import urllib.request
from secure import TOKEN

import requests
import pandas as pd
from bs4 import BeautifulSoup
import csv


def get_filings(start_from=0):
    # API Key
    #     TOKEN = '__'
    API = "https://api.sec-api.io?token=" + TOKEN

    # define the filter parameters you want to send to the API
    payload = {
        "query": {
            "query_string": {
                "query": "formType:\"S-1\""
            }
        },
        "from": f"{start_from}",
        "size": "200",
        "sort": [
            {
                "filedAt": {
                    "order": "desc"
                }
            }
        ]
    }

    # format your payload to JSON bytes
    jsondata = json.dumps(payload)
    jsondataasbytes = jsondata.encode('utf-8')  # needs to be bytes

    # instantiate the request
    req = urllib.request.Request(API)

    # set the correct HTTP header: Content-Type = application/json
    req.add_header('Content-Type', 'application/json; charset=utf-8')
    # set the correct length of your request
    req.add_header('Content-Length', len(jsondataasbytes))

    # send the request to the API
    response = urllib.request.urlopen(req, jsondataasbytes)

    # read the response
    res_body = response.read()
    # transform the response into JSON
    filings = json.loads(res_body.decode("utf-8"))
    return pd.DataFrame(filings['filings'])


def get_html(url):
    """Takes url and returns html"""
    headers = ({'User-Agent':
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                    'Chrome/58.0.3029.110 Safari/537.36',
                'Accept-Language': 'en-US, en;q=0.5'})
    r = requests.get(url, headers=headers, verify=False)
    if r.ok:
        return r.text
    print(r.status_code)



















def get_report_tables(html, report_name):
    """Takes html and report_name (title of financial statements).
     Returns list of tables in div tags having report_name in text"""
    soup = BeautifulSoup(html, 'lxml')
    tables = [table
              for div in soup.find_all('div') if report_name.lower() in div.text.lower()
              for table in div.find_all('table')]
    return tables


def find_field_in_tables(tables, field_name):
    """iterates over all tables in the list of tables until it finds a value for field_name
    if no value is found, then returns a None value for field_name

    tables - list of soup objects
    field_name - name of field in corresponding finantial statement
    returns -> field_name, value"""
    for table in tables:
        try:
            field, value = list(find_field_in_table(
                table, field_name).items())[0]
            if isinstance(value, (float, int)):
                return field_name, value
        except:
            continue
    return field_name, None


def find_field_in_table(table, field_name):
    """
    Finds field_name in the table and returns its value.
    Returns result in dictionary {field_name: value}
    """
    trs = table.find_all('tr')
    result = {}
    for tr in trs:
        tds = tr.find_all('td')
        try:
            name = tds[0].text.replace(':', '').strip().lower()
        except:
            name = ''
        if field_eq_text(field_name, name):
            try:
                value = find_numeric(tds)
                result[name] = value
                return result
            except:
                value = ''
            result[name] = value
            if value != '':
                return result
    return None


def field_eq_text(field_name, text):
    if isinstance(field_name, list):
        for item in field_name:
            if item.lower() == text.lower():
                return field_name
    else:
        if field_name.lower() == text.lower():
            return field_name
    return None


def refine_value(value):
    value = value.strip().replace(',', '').replace('$', '')
    if value != '' and value[0] == '(':
        value = '-' + value.replace('(', '').replace(')', '')
    try:
        return float(value)
    except:
        return ''


def find_numeric(tds):
    for i in range(1, len(tds)):
        value = refine_value(tds[i].text)
        if isinstance(value, float):
            return value
    return ''


def get_value_from_html(html, report_name, field_name):
    """returns field,value pair from html
    input parameters:
        html        ->
        report_name -> name of the financial statement from the table header
                      ['Statement of Operations', 'Balance Sheet', 'Statement of Cash Flow']
        field_name -> field name from the financial statement table
                        for example: 'Revenue', ['Net Income', 'Net Loss', 'net income (loss)']

    Example:
        get_value_from_html(html, report_name='Balance Sheet', field_name='Cash and cash equivalents')

    """
    tables = get_report_tables(html, report_name=report_name)
    field, value = find_field_in_tables(tables, field_name)
    if isinstance(field, list):
        return field[0], value
    return field, value


def iterate_fields_dict(html, fields_dict):
    """
    Iterates
    fields_dict = {'Statement of Operations':['Revenue',
                                     ['Net Income', 'Net Loss', 'net income (loss)']],
          'Balance Sheet': ['Cash and cash equivalents',
                            'Goodwill',
                            'Intangible assets',
                            'Total assets',
                            'Commercial Paper',
                            'Other Current Borrowings',
                            ['Long Term Debt', 'current portion'],
                            'Short-Term Debt'],
          'Statement of Cash Flow': ['Net cash used in operating activities',
                                     ['Purchases of property and equipment', 'Proceeds from property and equipment']]}

    returns a dictionary of field name: value pairs
    """
    result = {}
    for report_name, field_names in fields_dict.items():
        for field_name in field_names:
            field, value = get_value_from_html(
                html, report_name=report_name, field_name=field_name)
            result[field] = value
    return result
