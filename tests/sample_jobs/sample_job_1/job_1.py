import pandas as pd
import requests
from bs4 import BeautifulSoup
from flask import Flask, request

app = Flask(__name__)

versions_and_sources = {}


@app.route("/scrape_versions_and_sources_from_table", methods=["POST"])
def scrape_versions_and_sources_from_table() -> dict:
    data = request.values.to_dict() if request.values else request.get_json()
    source_name = data.get("source_name")
    url = data.get("url")
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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
