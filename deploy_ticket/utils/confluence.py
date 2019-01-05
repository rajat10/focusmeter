from atlassian import Confluence

from common.config import BASE_URL
from common import credentials
from bs4 import BeautifulSoup


class MyConfluence(Confluence):
    """
    """

    def __init__(self, url, username, password, timeout):
        super().__init__(url, username, password, timeout)


confluence = MyConfluence(
    url=BASE_URL + '/wiki',
    username=credentials.CONFLUENCE_USERNAME,
    password=credentials.CONFLUENCE_PASSWORD,
    timeout=300
)

#
# status = confluence.create_page(
#     space='DEMO',
#     title='This is the title',
#     body='This is the body. You can use <strong>HTML tags</strong>!'
# )
status = confluence.get_page_by_id(page_id=18546708, expand='body')
confluence.get_page_by_id(page_id=18546708, expand='body.atlas_doc_format')

soup = BeautifulSoup(confluence.get_page_by_id(page_id=18546708, expand='body.view').get('body').get('view').get('value'), 'html.parser')

data = {}
table = soup.find('table')
table_body = table.find('tbody')
rows = table_body.find_all('tr')
for row in rows:
    cols = row.find_all('td')
    cols = [ele.text.strip() for ele in cols if ele.text.strip()]
    if cols:
        if cols[0] not in data:
            data[cols[0]] = []
        data[cols[0]].append(cols[1:])




status = confluence.get_page_by_title(space='TECH', title='Database Schema changes review')
confluence.get_page_space(18546708)

print(data)

print(status)

