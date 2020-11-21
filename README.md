s1-list.csv - датасет c url ссылками на формы s1
s1-result_1202.csv - результат парсинга финансовых отчётов из формы s1

get-s1-list.ipynb - ноутбук получения url на формы s1 через https://sec-api.io/
parse_S1_BS.ipynb - ноутбук с примером парсинга данных финансовых отчётов формы s1

1. Словарь с названиями финансовых отчётов и полей таблиц для парсинга
`python
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
`
2. iterate_fields_dict возвращает словарь с именами полей и из значениями из формы S1 
`python
url = 'https://www.sec.gov/Archives/edgar/data/1430306/000161577418011996/s113713_s1a.htm'
iterate_fields_dict(html=get_html(url), fields_dict=fields_dict)
`
