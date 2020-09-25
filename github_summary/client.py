from github import Github
from datetime import datetime, timedelta
from brewtils import command, parameter, system


@system
class GithubSummary:
    """A client that is designed to pull back summaries of Github Repos"""

    def __init__(self, params, username: str = None, password: str = None, token: str = None):

        if token:
            self.g = Github(token)
        elif username and password:
            self.g = Github(username, password)
        else:
            # If username/password or Token is not provided, github allows for a limited query
            # of their API. Running this will most likely exceed that hourly rate.
            self.g = Github()

    @command(output_type="HTML", description="Create summary PRs created/modified in date range")
    @parameter(
        key="organization",
        description="Github Organization",
        optional=False,
        type="String",
    )
    @parameter(
        key="repoName",
        description="Github Repo Name",
        optional=False,
        type="String",
    )
    @parameter(
        key="days",
        description="How many days back to query",
        optional=True,
        type="Integer",
        default=30,
    )
    @parameter(
        key="base",
        description="Branch",
        optional=True,
        type="String",
        default="master",
    )
    def get_latest_active_prs(self, organization: str, repoName: str, days: int = 30, base: str = "master"):
        repo = self.g.get_repo(f'{organization}/{repoName}')

        pulls = repo.get_pulls(state='open', sort='created', base=base)

        now = datetime.now()

        response = ""
        for pr in pulls:
            if now - timedelta(days=days) <= pr.updated_at <= now and not pr.user.login.endswith("-bot"):
                response += f"<h3>{organization}/{repoName}#{pr.number} {pr.title}</h3>" \
                            f"<i>Created: {pr.user.name if pr.user.name else pr.user.login} </i><br>" \
                            f"{pr.body}<br>"

        return response

    @command(output_type="HTML", description="Create summary PRs closed in date range")
    @parameter(
        key="organization",
        description="Github Organization",
        optional=False,
        type="String",
    )
    @parameter(
        key="repoName",
        description="Github Repo Name",
        optional=False,
        type="String",
    )
    @parameter(
        key="days",
        description="How many days back to query",
        optional=True,
        type="Integer",
        default=30,
    )
    @parameter(
        key="base",
        description="Branch",
        optional=True,
        type="String",
        default="master",
    )
    def get_latest_closed_prs(self, organization: str, repoName: str, days: int = 14, base: str = "master"):
        repo = self.g.get_repo(f'{organization}/{repoName}')

        pulls = repo.get_pulls(state='closed', sort='created', base=base)

        now = datetime.now()

        response = ""
        for pr in pulls:
            if now - timedelta(days=days) <= pr.updated_at <= now and not pr.user.login.endswith("-bot"):
                response += f"<h3>{organization}/{repoName}#{pr.number} {pr.title}</h3>" \
                            f"<i>Created:{pr.user.name if pr.user.name else pr.user.login} </i><br>" \
                            f"{pr.body}<br>"

        return response

    @command(output_type="HTML", description="Grabs PRs in date range and provides open/closed data")
    @parameter(
        key="organization",
        description="Github Organization",
        optional=False,
        type="String",
    )
    @parameter(
        key="repoName",
        description="Github Repo Name",
        optional=False,
        type="String",
    )
    @parameter(
        key="days",
        description="How many days back to query",
        optional=True,
        type="Integer",
        default=30,
    )
    @parameter(
        key="base",
        description="Branch",
        optional=True,
        type="String",
        default="master",
    )
    def get_pr_open_closed(self, organization: str, repoName: str, days: int, base: str, ):
        repo = self.g.get_repo(f'{organization}/{repoName}')

        pulls = repo.get_pulls(state='closed', sort='created', base=base)

        now = datetime.now()

        response = "<table><th><td>PR</td><td>Developer</td><td>Open Date</td><td>Closed Date<td><th>"
        for pr in pulls:
            if now - timedelta(days=days) <= pr.updated_at <= now and not pr.user.login.endswith("-bot"):
                response += f"<tr><td>{organization}/{repoName}#{pr.number} {pr.title}</td>" \
                            f"<td>{pr.user.name if pr.user.name else pr.user.login} </td>" \
                            f"<td>{pr.created_at}</td>" \
                            f"<td>{pr.merged_at}</td></tr>"

        response += "</table>"
        return response

    def generate_timestamp(self, date: datetime):
        return f"{date.isocalendar()[0]}-W{date.isocalendar()[1]}"

    def get_week_start(self, date: datetime):

        week = f"{date.isocalendar()[0]}-W{date.isocalendar()[1]}"

        r = datetime.strptime(week + '-1', "%Y-W%W-%w")

        return f"{r.date().isoformat()}"

    @command(output_type="HTML", description="Grabs PRs in date range and provides open/closed data")
    @parameter(
        key="organization",
        description="Github Organization",
        optional=False,
        type="String",
    )
    @parameter(
        key="repoName",
        description="Github Repo Name",
        optional=False,
        type="String",
    )
    @parameter(
        key="days",
        description="How many days back to query",
        optional=True,
        type="Integer",
        default=30,
    )
    @parameter(
        key="base",
        description="Branch",
        optional=True,
        type="String",
        default="master",
    )
    def get_pr_daily_metrics(self, organization: str, repoName: str, days: int, base: str, ):
        repo = self.g.get_repo(f'{organization}/{repoName}')

        closedPulls = repo.get_pulls(state='closed', sort='created', base=base)

        openPulls = repo.get_pulls(state='closed', sort='created', base=base)

        now = datetime.now()

        stats = {}

        for pr in closedPulls:
            if now - timedelta(days=days) <= pr.updated_at <= now and not pr.user.login.endswith("-bot"):

                created = self.generate_timestamp(pr.created_at)

                if created in stats:
                    stats[created]['created'] = stats[created]['created'] + 1
                else:
                    stats[created] = {}
                    stats[created]['created'] = 1
                    stats[created]['merged'] = 0
                    stats[created]['date'] = self.get_week_start(pr.created_at)

                if pr.merged_at:
                    merged = self.generate_timestamp(pr.merged_at)
                    if merged in stats:
                        stats[merged]['merged'] = stats[merged]['merged'] + 1
                    else:
                        stats[merged] = {}
                        stats[merged]['created'] = 0
                        stats[merged]['merged'] = 1
                        stats[merged]['date'] = self.get_week_start(pr.merged_at)

        for pr in openPulls:
            if now - timedelta(days=days) <= pr.updated_at <= now and not pr.user.login.endswith("-bot"):

                created = self.generate_timestamp(pr.created_at)

                if created in stats:
                    stats[created]['created'] = stats[created]['created'] + 1
                else:
                    stats[created] = {}
                    stats[created]['created'] = 1
                    stats[created]['merged'] = 0
                    stats[created]['date'] = self.get_week_start(pr.created_at)

                if pr.merged_at:
                    merged = self.generate_timestamp(pr.merged_at)
                    if merged in stats:
                        stats[merged]['merged'] = stats[merged]['merged'] + 1
                    else:
                        stats[merged] = {}
                        stats[merged]['created'] = 0
                        stats[merged]['merged'] = 1
                        stats[merged]['date'] = self.get_week_start(pr.merged_at)

        # print(stats)
        response = "<table>" \
                   "<tr>" \
                   "<td>Week</td>" \
                   "<td>Date</td>" \
                   "<td>Total Open</td>" \
                   "<td>Total Closed</td>" \
                   "<tr>"

        for day in stats:
            response += "<tr>"
            response += f"<td>{day}</td>"
            response += f"<td>{stats[day]['date']}</td>"
            response += f"<td>{stats[day]['created']}</td>"
            response += f"<td>{stats[day]['merged']}</td>"
            response += "</tr>"
        response += "</table>"
        return response

    @command(output_type="HTML", description="Create summary tickets created in date range")
    @parameter(
        key="organization",
        description="Github Organization",
        optional=False,
        type="String",
    )
    @parameter(
        key="repoName",
        description="Github Repo Name",
        optional=False,
        type="String",
    )
    @parameter(
        key="days",
        description="How many days back to query",
        optional=True,
        type="Integer",
        default=30,
    )
    def get_latest_created_tickets(self, organization: str, repoName: str, days: int = 14):
        repo = self.g.get_repo(f'{organization}/{repoName}')

        open_issues = repo.get_issues(state='open')
        now = datetime.now()

        response = ""
        for issue in open_issues:
            if now - timedelta(days=days) <= issue.created_at <= now and not issue.user.login.endswith("-bot"):
                response += f"<h3>{organization}/{repoName}#{issue.number} {issue.title}</h3>" \
                            f"<i>Created: {issue.user.name if issue.user.name else issue.user.login} </i><br>" \
                            f"<i>Assigned: {issue.assignee.login if issue.assignee else ''} </i><br>" \
                            f"{issue.body}<br>"

        return response

    @command(output_type="HTML", description="Create summary tickets closed in date range")
    @parameter(
        key="organization",
        description="Github Organization",
        optional=False,
        type="String",
    )
    @parameter(
        key="repoName",
        description="Github Repo Name",
        optional=False,
        type="String",
    )
    @parameter(
        key="days",
        description="How many days back to query",
        optional=True,
        type="Integer",
        default=30,
    )
    def get_latest_closed_tickets(self, organization: str, repoName: str, days: int = 14):
        repo = self.g.get_repo(f'{organization}/{repoName}')

        open_issues = repo.get_issues(state='closed')
        now = datetime.now()

        response = ""
        for issue in open_issues:
            if now - timedelta(days=days) <= issue.closed_at <= now and not issue.user.login.endswith("-bot"):
                response += f"<h3>{organization}/{repoName}#{issue.number} {issue.title}</h3>" \
                            f"<i>Created: {issue.user.name if issue.user.name else issue.user.login} </i><br>" \
                            f"<i>Assigned: {issue.assignee.login if issue.assignee else ''} </i><br>" \
                            f"{issue.body}<br>"

        return response

    @command(output_type="JSON", description="List of all Repos in an Organization")
    @parameter(
        key="organization",
        description="Github Organization",
        optional=False,
        type="String",
    )
    def get_repos_by_organization(self, organization):
        organization = self.g.get_organization(organization)
        repos = organization.get_repos()

        repo_names = list()
        for repo in repos:
            repo_names.append(repo.name)

        return repo_names

    @command(output_type="HTML", description="Create summary for a single Repo")
    @parameter(
        key="organization",
        description="Github Organization",
        optional=False,
        type="String",
    )
    @parameter(
        key="repoName",
        description="Github Repo Name",
        optional=False,
        type="String",
    )
    @parameter(
        key="days",
        description="How many days back to query",
        optional=True,
        type="Integer",
        default=30,
    )
    @parameter(
        key="base",
        description="Branch",
        optional=True,
        type="String",
        default="master",
    )
    def get_repo_summary(self, organization: str, repoName: str, days: int = 14, base: str = "master"):

        open_prs = self.get_latest_active_prs(organization, repoName, days=days, base=base)
        closed_prs = self.get_latest_closed_prs(organization, repoName, days=days, base=base)
        opened_tickets = self.get_latest_created_tickets(organization, repoName, days=days)
        closed_tickets = self.get_latest_closed_tickets(organization, repoName, days=days)

        if open_prs or closed_prs or opened_tickets or closed_tickets:
            response = f"<h1>Summary for {organization}/{repoName}</h1>"

            if open_prs:
                response += f"<h2>Open PRs</h2>" \
                            f"{open_prs}"
            if closed_prs:
                response += f"<h2>Closed PRs</h2>" \
                            f"{closed_prs}"
            if opened_tickets:
                response += f"<h2>Open Tickets</h2>" \
                            f"{opened_tickets}"

            if closed_tickets:
                response += f"<h2>Closed Tickets</h2>" \
                            f"{closed_tickets}"

            return response
        else:
            return ""

    @command(output_type="HTML", description="Create summary for all repos in an organization")
    @parameter(
        key="organization",
        description="Github Organization",
        optional=False,
        type="String",
    )
    @parameter(
        key="days",
        description="How many days back to query",
        optional=True,
        type="Integer",
        default=30,
    )
    @parameter(
        key="base",
        description="Branch",
        optional=True,
        type="String",
        default="master",
    )
    def get_organization_summary(self, organization, days: int = 14, base: str = "master"):

        response = ""
        for repo in self.get_repos_by_organization(organization):
            response += self.get_repo_summary(organization, repo, days=days, base=base)

        return response

    @command(output_type="HTML",
             description="Create summary for all Projects in an organization (or organization/repo)")
    @parameter(
        key="organization",
        description="Github Organization",
        optional=False,
        type="String",
    )
    @parameter(
        key="repo",
        description="Github Repo",
        optional=True,
        type="String",
        default=''
    )
    def get_projects_issues_summary(self, organization, repo: str = None):

        organization = self.g.get_organization(organization)
        projects = []
        if repo != '':
            repos = organization.get_repo(repo)
            projects_pages = repos.get_projects()
        else:
            projects_pages = organization.get_projects()

        result = '<table datatable="ng"' \
                 '       dt-options="dtOptions"' \
                 '       class="table table-striped table-bordered"' \
                 '       style="width: 100%">' \
                 '  <thead>' \
                 '    <tr>' \
                 '      <th scope="col">Organization</th>' \
                 '      <th scope="col">Project</th>' \
                 '      <th scope="col">Status</th>' \
                 '      <th scope="col">Issue #</th>' \
                 '      <th scope="col">Title</th>' \
                 '      <th scope="col">Description</th>' \
                 '    </tr>' \
                 '  </thead>' \
                 '  <tbody>'

        for project in projects_pages:
            projects.append(project)
            for column in project.get_columns():
                for card in column.get_cards():
                    issue = card.get_content()
                    result += '<tr>' \
                              '  <td>' + organization.name + '</td>' \
                                                             '  <td>' + project.name + '</td> ' \
                                                                                       '  <td>' + column.name + '</td> ' \
                                                                                                                '  <td>' + str(
                        issue.number) + '</td> ' \
                                        '  <td>' + issue.title + '</td> ' \
                                                                 '  <td>' + issue.body + '</td>' \
                                                                                         '</td>'

        result += '</tbody>' \
                  '</table>'
        return result
