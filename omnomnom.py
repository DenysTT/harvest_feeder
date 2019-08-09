import json
import requests
import logging
import sys
import pandas as pd
from datetime import datetime, timedelta
import os

log = logging.getLogger('omnomnom')
logpattern = '%(asctime)s %(levelname)s %(message)s'
log_handler = logging.StreamHandler()
log_handler.setFormatter(logging.Formatter(logpattern))
log.addHandler(log_handler)
log.setLevel(logging.DEBUG)

base_url = "https://api.harvestapp.com/"
url_add_time_entry = base_url + "v2/time_entries"
url_get_me = base_url + "/v2/users/me"
url_my_projects = base_url + "v2/users/%s/project_assignments"
url_my_entries = base_url + "/v2/time_entries"
headers = {
    "User-Agent": "Python Harvest API Sample",
    "Authorization": "Bearer " + os.environ.get("HARVEST_ACCESS_TOKEN"),
    "Harvest-Account-ID": os.environ.get("HARVEST_ACCOUNT_ID")
}
template = {
    "Mon": {
        "TECH-011 Devops - BAU Requests": {
         "Programming": 8
        }
    },
    "Tue": {
        "TECH-011 Devops - BAU Requests": {
            "Programming": 8
        }
    },
    "Wed": {
        "TECH-011 Devops - BAU Requests": {
            "Programming": 8
        }
    },
    "Thu": {
        "TECH-011 Devops - BAU Requests": {
            "Programming": 8
        }
    },
    "Fri": {
        "TECH-011 Devops - BAU Requests": {
            "Programming": 8
        }
    }
}


def get_user_id():
    rsp = requests.get(url_get_me,
                       headers=headers
                       )
    if rsp.status_code != 200:
        log.error(rsp.text)
        sys.exit(1)
    log.debug(rsp.text)
    rsp_json = json.loads(rsp.content)
    return rsp_json['id']


def get_project_id(id, project_name):
    rsp = requests.get(url_my_projects % id,
                       headers=headers
                       )
    if rsp.status_code != 200:
        log.error(rsp.text)
        sys.exit(1)
    log.debug(rsp.text)
    rsp_json = json.loads(rsp.content)
    return [x for x in rsp_json['project_assignments'] if x['project']['name'] == project_name][0]


def add_time_entry(user_id, project_id, task_id, hours, date):
    data = {"user_id": user_id,
            "project_id": project_id,
            "task_id": task_id,
            "spent_date": date,
            "hours": hours}
    rsp = requests.post(url_my_entries,
                        headers=headers,
                        data=data
                        )
    if rsp.status_code != 200:
        log.error(rsp.text)
        sys.exit(1)
    log.debug(rsp.text)
    rsp_json = json.loads(rsp.content)
    return rsp_json


def get_task_id(project):
    return [x for x in project['task_assignments'] if x['task']['name'] == 'Programming'][0]['task']['id']

def get_dates():
    day = datetime.today().strftime("%d/%m/%Y")
    dt = datetime.strptime(day, '%d/%m/%Y')
    start_date = dt - timedelta(days=dt.weekday())
    end_date = start_date + timedelta(days=6)
    return pd.bdate_range(start=start_date, end=end_date)

def main():
    work_dates = get_dates()
    user_id = get_user_id()
    for dates, timesheets in zip(work_dates, template.items()):
        for day in timesheets:
            project = get_project_id(user_id, "TECH-011 Devops - BAU Requests")
            project_id = project['project']['id']
            task_id = get_task_id(project)
            hours = 8.0
            date = dates._date_repr
            add_time_entry(user_id, project_id, task_id, hours, date)


# rsp_json = json.loads(rsp.content)
# print(json.dumps(rsp_json, sort_keys=True, indent=4))


if __name__ == "__main__":
    main()
