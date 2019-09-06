import datetime
import webbrowser as wb

import camelot
from ics import Calendar, Event

import numpy as np
import ruamel.yaml
import schoolopy
from pyaml import pprint


def get_date(partial_date):
    """
    Creates datetime object from weekday + month and day string, e.g. Tue
    9/4 turns into datetime(2019/2020, 9, 4, 14, 20) -- ignores the weekday
    ("Tue") in the string. Calc class is always at 14:20:00.
    """
    month, day = partial_date.split()[1].split('/')
    year = 2020 if int(month) < 9 else 2019
    dt = datetime.datetime(int(year), int(month), int(day), hour=14,
                           minute=20)
    return dt


def is_empty(cell):
    return bool(cell.strip())


def get_df_from_pdf(path, first_row_to_header=True):
    """
    Converts pdf to dataframe, allows for setting first row as the header
    if not recognized properly by camelot.
    """
    tables = camelot.read_pdf(path)

    df = tables[0].df

    if first_row_to_header:
        df.columns = df.iloc[0]
        return df[1:]
    return df


def get_events_from_study_guide(filename):
    """
    Gets events from Walton study guide, turns to dataframe, then creates
    dictionaries for each event and put all dicts in list.
    """

    df = get_df_from_pdf(filename)

    # slice df only where df['Due'] is not empty, then save to_dict,
    # orient='records' to create a separate dict with all keys for each event
    assignments = df[df['Due Date'].apply(is_empty)].to_dict(orient='records')

    events = []
    for hw in assignments:
        title = 'Section ' + hw['Section']
        desc = hw['Topic'].replace('\n', '') + '\nProblems: ' \
               + hw['Exercises'].replace('\n', '')
        date = get_date(hw['Due Date'])

        event = {
            "title": title,
            "description": desc,
            "begin": date,
        }

        events.append(event)

    return events


def get_schedule():
    """
    Gets class schedule, splits into fire and hawek weeks.
    :return: Fire and Hawk week dataframes
    """
    df = get_df_from_pdf("classes_and_schedule.pdf", first_row_to_header=False)
    print(df.columns)

    times = df[0]  # just the times column, save because dropping it

    df.drop(0, axis=1, inplace=True)

    n = 5  # days in week, split df into two halves
    fire_week, hawk_week = np.split(
        df,
        indices_or_sections=np.arange(start=n, stop=len(df.columns), step=n),
        axis=1
    )

    days_of_week = list(range(0, 5))
    # rename columns to numbers, for easy use with datetime.weekday()
    fire_week.columns = days_of_week
    hawk_week.columns = days_of_week

    return fire_week, hawk_week


def create_ical(events_dict):
    """Creates an iCalendar object, populates with events and returns."""
    iCal = Calendar()

    for event in events_dict:
        e = Event()
        e.name = event['title']
        e.description = event['description']
        e.begin = event['begin']
        iCal.events.add(e)

    return iCal


events = get_events_from_study_guide("/Users/Sam/Documents/Shalhevet/2019-2020/Precalculus/APC_Ch10_D_Block_1819.pdf")

cal = create_ical(events)
with open('112course_schedule.ics', 'w') as f:
    f.writelines(cal)
