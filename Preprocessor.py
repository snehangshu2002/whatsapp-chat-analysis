import re
import pandas as pd

def preprocess(data):
    # Pattern to match both 24-hour and 12-hour (with or without am/pm) time formats
    pattern = r'\d{1,2}/\d{1,2}/\d{2}, \d{1,2}:\d{2}(?:\u202f?(?:am|pm))? - '
    messages = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)
    df = pd.DataFrame({'date': dates, 'message': messages})

    # Try parsing with both 24-hour and 12-hour formats
    def parse_date(date_str):
        for fmt in ['%d/%m/%y, %I:%M\u202f%p - ', '%d/%m/%y, %H:%M - ', '%m/%d/%y, %H:%M - ', '%m/%d/%y, %I:%M\u202f%p - ']:
            try:
                return pd.to_datetime(date_str, format=fmt)
            except Exception:
                continue
        return pd.NaT

    df["date"] = df["date"].apply(parse_date)

    # Separate users and messages from the 'message' column
    users = []
    messages_text = []

    for msg in df['message']:
      entry = re.split(r'^(.*?):\s', msg)
      if len(entry) == 3:
        users.append(entry[1])
        messages_text.append(entry[2])
      else:
        users.append('group_notification')
        messages_text.append(msg)

    df['user'] = users
    df['message'] = messages_text 
    df["year"]=df["date"].dt.year
    df["month"]=df["date"].dt.month_name()
    df["month_num"]=df["date"].dt.month
    df["only_date"]=df["date"].dt.date
    df["day_name"]=df["date"].dt.day_name()
    df["day"]=df["date"].dt.day
    df["hour"]=df["date"].dt.hour
    df["minute"]=df["date"].dt.minute
    df["second"]=df["date"].dt.second
    df["day_name"]=df["date"].dt.day_name()

    period = []
    for hour in df[['day_name', 'hour']]['hour']:
        if hour == 23:
            period.append(str(hour) + "-" + str('00'))
        elif hour == 0:
            period.append(str('00') + "-" + str(hour + 1))
        else:
            period.append(str(hour) + "-" + str(hour + 1))
    df["period"]=period

    return df
