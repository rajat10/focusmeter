from deploy_ticket.utils.confluence import get_db_queries_for_infra_tickets
from deploy_ticket.utils.jira_util import get_latest_sprint_issues


class CreateUpd(object):
    """
    """
    udp_title = ""
    db_schema_confluence_page_id = None

    def __init__(self, db_schema_confluence_page_id):
        """
        """
        self.db_schema_confluence_page_id = db_schema_confluence_page_id

    def _create_db_changes_infra_tickets(self):
        """
        :return:
        """
        latest_sprint_issues = get_latest_sprint_issues()
        db_queries_by_issues = get_db_queries_for_infra_tickets(page_id=self.db_schema_confluence_page_id)
        print("hello")


a = CreateUpd(db_schema_confluence_page_id=18546708)
a._create_db_changes_infra_tickets()

upd_v2_deployment_4_dec = 407371807