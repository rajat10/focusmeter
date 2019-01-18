import os

from atlassian import Confluence
from django.template.loader import render_to_string


from common.config import BASE_URL, DATABASE_SCHEMA_CHANGE_CONFLUENCE_PAGE, CONFLUENCE_SPACE_FOR_PUSH_DEPLOYMENT_TICKET
from common import credentials
from bs4 import BeautifulSoup

from deploy_ticket.models import PushDeployment, Issue, ConfluenceWikiPage


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




def get_db_queries_for_infra_tickets(page_id=DATABASE_SCHEMA_CHANGE_CONFLUENCE_PAGE):
    """
    :return:
    """
    confluence.get_page_by_id(page_id=page_id, expand='body.atlas_doc_format')

    soup = BeautifulSoup(
        confluence.get_page_by_id(page_id=page_id, expand='body.view').get('body').get('view').get('value'),
        'html.parser')

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
            data[cols[0]].append({'notes': cols[1] if len(cols)==3 else '', 'db_script': cols[2 if len(cols)==3 else 1]})
    return data


def create_wiki(push_deployment):
    body_str = render_to_string(
        template_name='../templates/ticket_format/upd/wiki.html',
        context={
            'release_date': push_deployment.scheduled_release_date,
            'scheduled_release_time': push_deployment.scheduled_release_time,
            'scheduled_maintainance_window': push_deployment.scheduled_maintainance_window,
            'sprint_date': push_deployment.releasing_sprint_display_name,
            'ticket_summary': Issue.objects.filter(
                sprint__push_deployment=push_deployment,
                selected_for_push_deployment=True,
                push_deployment_db_ticket=None,
                push_deployment_main_ticket=None
            ).all(),
            'uat_servers': push_deployment.get_server_list(),
            'artifact_link': push_deployment.artifact_link,
            'installation_file_link': push_deployment.installation_file_link,
            'installation_file_name': os.path.basename(push_deployment.installation_file_link),
            'artifact_file_name': os.path.basename(push_deployment.artifact_link)
        }
    )
    print(body_str)
    wiki_page = confluence.update_page(
        page_id=413532488,
        parent_id=3735630,
        title='This is the title to test please dont execute any steps.',
        body=body_str
    )
    # wiki_page = confluence.create_page(
    #     space=CONFLUENCE_SPACE_FOR_PUSH_DEPLOYMENT_TICKET,
    #     title='This is the title to test please dont execute any steps.',
    #     parent_id=3735630,
    #     body=body_str
    # )
    if wiki_page:
        ConfluenceWikiPage.objects.update_or_create(
            space=CONFLUENCE_SPACE_FOR_PUSH_DEPLOYMENT_TICKET,
            page_id=wiki_page.get('id'),
            defaults={
                'title': wiki_page.get('title'),
                'body': body_str,
                'push_deployment': push_deployment,
                'ui_link': wiki_page['_links']['base'] + wiki_page['_links']['webui']
            }
        )
        # ConfluenceWikiPage.objects.create(
        #     title=wiki_page.get('title'),
        #     body=body_str,
        #     push_deployment=push_deployment
        # )
    print(wiki_page)


def create_deployment_wiki_tickets(push_deployment):
    """
    :return:
    """
    create_wiki(push_deployment=push_deployment)

# status = confluence.get_page_by_title(space='TECH', title='Database Schema changes review')
# confluence.get_page_space(18546708)
#
# print(status)

