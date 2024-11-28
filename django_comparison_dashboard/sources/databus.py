import logging
import math
from io import BytesIO

import pandas as pd
import requests

from django_comparison_dashboard import forms, settings
from django_comparison_dashboard.sources import core

DATABUS_ENDPOINT = "https://databus.openenergyplatform.org/sparql"
DATABUS_COLLECTION_URL = "https://databus.openenergyplatform.org/sedos-project/collections/sedos_results"


class DatabusScenario(core.Scenario):
    source_name = "Databus"

    def __init__(self, scenario_id: str):
        super().__init__(scenario_id, settings.DataType.Scalar)


class DatabusDataSource(core.DataSource):
    name = "Databus"
    scenario = DatabusScenario
    form = forms.DatabusSourceUploadForm

    @classmethod
    def list_scenarios(cls) -> list[core.Scenario]:
        return [DatabusScenario(artifact) for artifact in get_artifacts_from_collection()]

    @classmethod
    def download_scenario(cls, scenario: DatabusScenario) -> pd.DataFrame:
        """
        Download scenario data from Databus using scenario version.

        Returns
        -------
        pd.DataFrame
            holding scenario data
        """
        logging.info(f"Requesting data for scenario '{scenario}' (Source: {cls.name})...")
        # TODO:
        #  Add download of latest scenario data. Use downloading artifact from data_adapter.
        #  See MODEX Source for extracting data as well.
        latest_version = get_latest_version_of_artifact(scenario.id)
        filenames = get_artifact_filenames(scenario.id, latest_version)
        data_url = [f for f in filenames if f.endswith(".csv")][0]
        csv_bytes = download_artifact(data_url)
        csv_buffer = BytesIO(csv_bytes)
        df = pd.read_csv(csv_buffer)
        df.drop("id", inplace=True, axis=1)
        df.replace(math.nan, None, inplace=True)
        return df


def query_sparql(query: str) -> dict:
    """
    Query SPARQL endpoint and return data as dict.

    Parameters
    ----------
    query: str
        SPARQL query to be executed

    Returns
    -------
    dict
        SPARQL results as dict
    """
    response = requests.post(
        DATABUS_ENDPOINT,
        headers={"Accept": "application/json, text/plain, */*", "Content-Type": "application/x-www-form-urlencoded"},
        data={"query": query},
        timeout=90,
    )
    data = response.json()
    return data["results"]["bindings"]


def get_artifacts_from_collection() -> list[str]:
    """Returns list of all artifacts found in given collection.

    Returns
    -------
    List[str]
        List of artifacts in collection
    """

    def extract_artifact_from_uri(uri: str):
        https, _, host, user, group, artifact, version, name = uri.split("/")
        return "/".join((https, _, host, user, group, artifact))

    response = requests.get(DATABUS_COLLECTION_URL, headers={"Accept": "text/sparql"}, timeout=90)
    result = query_sparql(response.text)
    files = {extract_artifact_from_uri(file["file"]["value"]) for file in result}
    return list(files)


def get_latest_version_of_artifact(artifact: str) -> str:
    """Returns the latest version of given artifact.

    Parameters
    ----------
    artifact: str
        DataId of artifact to check version of

    Returns
    -------
    str
        Latest version of given artifact
    """

    def get_version_number(v: str) -> str | int:
        """
        Try to read version number from version string

        Parameters
        ----------
        v: str
            Version as string

        Returns
        -------
        str | int
            If version number can be extracted int is returned, otherwise version is returned as is
        """
        if "v" not in v:
            return v
        try:
            return int(v[1:])
        except ValueError:
            return v

    query = f"""
        PREFIX rdfs:   <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX rdf:    <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX dcat:   <http://www.w3.org/ns/dcat#>
        PREFIX dct:    <http://purl.org/dc/terms/>
        PREFIX dcv:    <https://dataid.dbpedia.org/databus-cv#>
        PREFIX dataid: <https://dataid.dbpedia.org/databus#>
        SELECT ?version WHERE
        {{
            GRAPH ?g
            {{
                ?dataset dataid:artifact <{artifact}> .
                ?dataset dct:hasVersion ?version .
            }}
        }} ORDER BY DESC (?version)
        """
    result = query_sparql(query)
    versions = [version["version"]["value"] for version in result]
    return sorted(versions, key=get_version_number)[-1]


def get_artifact_filenames(artifact: str, version: str) -> list[str]:
    query = f"""
        PREFIX rdfs:   <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX rdf:    <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX dcat:   <http://www.w3.org/ns/dcat#>
        PREFIX dct:    <http://purl.org/dc/terms/>
        PREFIX dcv:    <https://dataid.dbpedia.org/databus-cv#>
        PREFIX dataid: <https://dataid.dbpedia.org/databus#>
        SELECT ?file WHERE
        {{
            GRAPH ?g
            {{
                ?dataset dataid:artifact <{artifact}> .
                ?distribution <http://purl.org/dc/terms/hasVersion> '{version}' .
                ?distribution dataid:file ?file .
            }}
        }}
        """
    result = query_sparql(query)
    return [file["file"]["value"] for file in result]


def download_artifact(artifact_file: str):
    """Downloads an artifact file.

    Parameters
    ----------
    artifact_file: str
        URI to artifact file

    Raises
    ------
    FileNotFoundError
        if request fails
    """
    response = requests.get(artifact_file, timeout=90)
    if response.status_code != 200:
        raise FileNotFoundError(f"Could not find artifact file '{artifact_file}'")
    return response.content
