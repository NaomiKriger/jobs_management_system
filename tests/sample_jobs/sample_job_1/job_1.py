import argparse

import pandas as pd
import requests
from bs4 import BeautifulSoup

versions_and_sources = {}


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source_name", required=True, help="source name")
    parser.add_argument("--url", required=True, help="url")
    args = parser.parse_args()

    source_name = args.source_name
    url = args.url
    if not source_name or not url or not isinstance(source_name, str) or not isinstance(url, str):
        return {}

    source = requests.get(url).text
    soup = BeautifulSoup(source, "html.parser")
    tables = soup.find_all("table", class_="styled-table")

    dict_to_update = {source_name: {}}

    for table in tables:
        current_table = pd.read_html(str(table))[0][["SOURCE", "VERSION"]]
        for index, row in current_table.iterrows():
            if row.VERSION not in dict_to_update[source_name]:
                dict_to_update[source_name].update({row.VERSION: {"source": row.SOURCE, "tested": False}})
            if len(dict_to_update[source_name]) >= 10:
                break
    versions_and_sources.update(dict_to_update)
    return versions_and_sources


run()
