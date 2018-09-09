import datetime as dt


def low_split(s):
    return "_".join(map(lambda x: x.lower(), s.split()))


def get_day_folder_path(days_diff=1):
    tommorow_date_str = (
                dt.date.today() + dt.timedelta(days=days_diff)).strftime(
        "%Y_%m_%d")
    path = f"/home/oleg/PycharmProjects/super8/data/{tommorow_date_str}"

    return path
