# TO DO
import pandas as pd
import json


def clean_col(col_name):
    return col_name.replace("_", " ").title().strip()


def load_dataframe(data_src, load_type='file'):
    from numpy import nan
    if load_type == 'file':
        with open(data_src, 'r', encoding='UTF-8') as f:
            data = json.loads(f.read())
    else:
        data = json.loads(data_src)
    df = pd.DataFrame.from_dict(data, orient='index')
    try:
        df.index = pd.to_datetime(df.index, unit='ms')
    except ValueError as e:
        df.index = pd.to_datetime(df.index, utc=True)
    cols = [clean_col(c) for c in df.columns]
    df.columns = cols
    for c in df.columns:
        df[c] = pd.to_numeric(df[c], errors='ignore')
    try:
        df['Dashboard Id'] = df['Dashboard Id'].fillna(-1)
        df['Dashboard Id'] = df['Dashboard Id'].astype(int).astype(str)
        df['Dashboard Id'] = df['Dashboard Id'].replace('-1', nan)
    except (ValueError, KeyError) as e:
        pass
    return df


def summarise(df):
    sources, dashboards, hasdata = [], [], False
    if 'Source' in df.columns:
        sources = list(df[df['Source'].notna()]['Source'].unique())
    timings = ['Acquire Connection', 'Cache Load', 'Execute Sql', 'Grand Total', 'Init', 'Marshalled Cache Load', 'Postprocess', 'Prepare', 'Setup', 'Stream', 'Stream Others', 'Stream This', 'Stream To Cache', 'Total', 'Unaccounted']
    timings = [t for t in timings if t in df.columns]
    if 'Dashboard Id' in df.columns:
        dashboards = list(df[df['Dashboard Id'].notna()]['Dashboard Id'].unique())
    records = len(df)
    numdays = len(set(df.index.date))
    if records > 0:
        hasdata = True
    return {"has_data": hasdata,
            "demo": False,
            "query_sources": sources,
            "timing_columns": timings,
            "dashboards": dashboards,
            "records": records,
            "numdays": numdays}


# Helper
def summarise_to_file(df, outfile):
    config = summarise(df)
    with open(outfile, 'w') as f:
        f.write(json.dumps(config))


def highcharts_timeseries(pd_json):
    """Converts a pandas json into a series array for highcharts"""
    series = []
    pd_json = json.loads(pd_json)
    for series_name, series_data in pd_json.items():
        staging = {"name": series_name, "data": []}
        for ix, val in series_data.items():
            staging['data'].append([int(ix), val])
        series.append(staging)
    return series


def highcharts_series(pd_json):
    """Converts a pandas json into labels and multiseries for stacked bar"""
    labels, series = [], []
    pd_json = json.loads(pd_json)
    one_time = True
    for series_name, series_data in pd_json.items():
        staging = {'name': series_name, 'data': []}
        if one_time:
            labels = [l for l in series_data.keys()]
            one_time = False
        staging['data'] = [v for v in series_data.values()]
        series.append(staging)
    return {"labels": labels, "series": series}


def daily_summary(df):
    try:
        return highcharts_timeseries(df.groupby(df.index.date)['Total'].describe()[['mean', '25%', '50%', '75%']].to_json())
    except Exception as e:
        return None


def bar_descending(df, colname='Process Id'):
    """Index and one measure"""
    try:
        return highcharts_series(df.groupby(colname)['Total'].mean().sort_values(ascending=False).to_json())
    except Exception as e:
        print(e)
        return None


def stacked_bar(df, colname='Process Id', limit=10):
    """Index and one measure, multi columns"""
    try:
        timings = ['Acquire Connection', 'Cache Load', 'Execute Sql', 'Grand Total', 'Init', 'Marshalled Cache Load', 'Postprocess', 'Prepare', 'Setup', 'Stream', 'Stream Others', 'Stream This', 'Stream To Cache', 'Total', 'Unaccounted']
        timings = [t for t in timings if t in df.columns]
        display = timings.copy()
        if 'Total' in display:
            display.remove('Total')
        return highcharts_series(df.groupby(colname).sum()[timings].sort_values(by='Total', ascending=False)[display].iloc[:limit].to_json())
    except Exception as e:
        print(e)
        return None

    # Helper
    def save_daily_summary(df, outfile):
        df = daily_summary(df)
        df.to_csv(outfile)


def read_config(df, request):
    """Take form request and perform the relevant analysis on a dataframe.
    Return a json with config_name: json_data"""
    row_limit = int(request['chartLimit'])
    daily_data = daily_summary(df)
    thread_performance = stacked_bar(df, 'Process Id', row_limit)
    dashboard_performance = stacked_bar(df, 'Dashboard Id', row_limit)
    source_performance = stacked_bar(df, 'Source', row_limit)
    summary = summarise(df)

    # Assemble output
    config = {'by_date': daily_data,
              'summary': summary,
              'thread_performance': thread_performance,
              'dashboard_performance': dashboard_performance,
              'source_performance': source_performance}
    return config

# if __name__ == '__main__':
#     import os
#     with open(os.path.join(os.path.expanduser('~'), 'Documents/python/looker/looker_log_performance_summary/parse_logs/app/demo/config.json'), 'r') as f:
#         data = json.loads(f.read())
#     print(data.keys())
