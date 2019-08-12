import json
import requests
import logging
import sys
from datetime import datetime, timedelta
import os

log = logging.getLogger('omnomnom')
logpattern = '%(asctime)s %(levelname)s %(message)s'
log_handler = logging.StreamHandler()
log_handler.setFormatter(logging.Formatter(logpattern))
log.addHandler(log_handler)
log.setLevel(logging.DEBUG)

TEMPLATE_FILE_NAME = os.environ.get("TEMPLATE_FILE_NAME")
base_url = "https://api.harvestapp.com/"
url_get_me = base_url + "/v2/users/me"
url_my_projects = base_url + "v2/users/%s/project_assignments"
url_my_entries = base_url + "v2/time_entries"
url_submit = "https://robmarlow.harvestapp.com/daily/review"
headers = {
    "User-Agent": "Python Harvest API",
    "Authorization": "Bearer " + os.environ.get("HARVEST_ACCESS_TOKEN"),
    "Harvest-Account-ID": os.environ.get("HARVEST_ACCOUNT_ID")
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
    if rsp.status_code != 201:
        log.error(rsp.text)
        sys.exit(1)
    log.debug(rsp.text)
    rsp_json = json.loads(rsp.content)
    return rsp_json


def get_task_id(project, task_name):
    return [x for x in project['task_assignments'] if x['task']['name'] == task_name][0]['task']['id']


def get_dates():
    day = datetime.today().strftime("%d/%m/%Y")
    dt = datetime.strptime(day, '%d/%m/%Y')
    start_date = dt - timedelta(days=dt.weekday())
    end_date = start_date + timedelta(days=6)
    delta = end_date - start_date  # as timedelta
    week = [start_date + timedelta(days=x) for x in range(delta.days + 1)]
    return [x for x in week if x.strftime("%A") not in ['Saturday', 'Sunday']]


def get_all_entries(params):
    rsp = requests.get(url_my_entries,
                        headers=headers,
                        params=params
                        )
    if rsp.status_code != 200:
        log.error(rsp.text)
        sys.exit(1)
    rsp_json = json.loads(rsp.content)
    return rsp_json


def remove_entries_if_available(range):
    params = {"from": range[0].strftime("%Y-%m-%d"),
              "to": range[4].strftime("%Y-%m-%d")}
    time_entries = get_all_entries(params)
    for entry in time_entries['time_entries']:
        rsp = requests.delete(url_my_entries + '/%s' % (entry['id']),
                              headers=headers
                              )
        if rsp.status_code != 200:
            log.error(rsp.text)
            sys.exit(1)
        log.debug(rsp.text)


def submit_weekly_report(user_id, dates):
    data = {"authenticity_token": "T___T",
            "submitted_date": dates[4].timetuple().tm_yday,
            "of_user": user_id,
            "submitted_date_year": dates[4].strftime("%Y"),
            "period_begin": dates[0].timetuple().tm_yday,
            "period_begin_year": dates[0].strftime("%Y"),
            "from_screen": "daily",
            "from_timesheet_beta": "true",
            "return_to": "/time/day/%s/%s/%s/%s" % (dates[0].strftime("%Y"), dates[0].strftime("%m"),
                                                    dates[0].strftime("%d"), user_id)
            }
    rsp = requests.post(url_submit,
                        headers=headers,
                        data=data
                        )
    if rsp.status_code != 200:
        log.error(rsp.text)
        sys.exit(1)

def main():
    user_id = get_user_id()
    work_dates = get_dates()
    remove_entries_if_available(work_dates)
    with open(TEMPLATE_FILE_NAME, 'r') as json_file:
        template = json.load(json_file)
    for date in work_dates:
        weekday_name = date.strftime("%A")
        workday_timeschedule = template[weekday_name]
        for project_name, tasks in workday_timeschedule.items():
            project = get_project_id(user_id, project_name)
            project_id = project['project']['id']
            for task, time in tasks.items():
                task_id = get_task_id(project, task)
                hours = float(time)
                work_date = date._date_repr
                add_time_entry(user_id, project_id, task_id, hours, work_date)
    submit_weekly_report(user_id, work_dates)


if __name__ == "__main__":
    main()
