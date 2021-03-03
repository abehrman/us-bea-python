import requests
import os
import json
import pprint

import pandas as pd

from _bea_token import * # imports BEA_API_TOKEN from .env file

# disable insecure HTTP request warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

user_ID = BEA_API_TOKEN

base_url = f"http://apps.bea.gov/api/data?&UserID={user_ID}&method=GETDATASETLIST&ResultFormat=JSON"


def _checkForError(results):
    if results['BEAAPI']['Results'].get('Error', None) is not None:
        print(results['BEAAPI']['Results']['Error']['APIErrorDescription'])
        print(pprint.pformat(results['BEAAPI']['Results']['Error']['AdditionalDetail'], indent=4))
        raise ValueError("Incorrect API specification.")


def getDataSetList() -> pd.DataFrame:
    """GetDataSetList – retrieves a list of the datasets currently offered

    Input
    ---------------------
    None

    Output
    ---------------------
    Returns a dataframe of lists
    """

    global user_ID

    method = "GETDATASETLIST"

    url = f"https://apps.bea.gov/api/data?&UserID={user_ID}&method={method}&ResultFormat=JSON"
    results = json.loads(getResult(url).content)

    _checkForError(results)

    dataSetTable = pd.DataFrame.from_dict(results['BEAAPI']['Results']['Dataset'])

    return dataSetTable

def getParameterList(dataSetName: str) -> pd.DataFrame:

    """ GetParameterList – retrieves a list of the parameters(required and optional) for a particular dataset.

    Input
    ----------------------
    dataSetName: str, example "Regional"

    Output
    ----------------------
    Returns pandas dataframe describing table query parameters
    """

    global user_ID

    method = "GETPARAMETERLIST"

    url = f"https://apps.bea.gov/api/data?&UserID={user_ID}&method={method}&datasetname={dataSetName}&ResultFormat=JSON"
    results = json.loads(getResult(url).content)

    _checkForError(results)

    paramTable = pd.DataFrame.from_dict(results['BEAAPI']['Results']['Parameter'])
    
    return paramTable

def getParameterValues(dataSetName: str, parameterName: str) -> pd.DataFrame:
    """GetParameterValues - retrives a list of the valid values for a particular parameter

    Input
    ---------------------
    dataSetName: str, example "IntlServTrade", options from getDataSetList()

    parameterName: str, example "TradeDirection", options from getParameterList(dataSetName)


    Returns
    ----------------------
    dataframe with descriptions and keys for descriptions of acceptable values for data pulls. Formally, 
    describes this result as a "ParamValue node with attributes that contain the actual permissable values
    (and usually a description of the value)."

    """
    global user_ID

    method = "GETPARAMETERVALUES"

    url = f"https://apps.bea.gov/api/data?&UserID={user_ID}" \
                f"&method={method}&" \
                f"&datasetname={dataSetName}" \
                f"&ParameterName={parameterName}" \
                "&ResultFormat=JSON"
    results = json.loads(getResult(url).content)
    
    _checkForError(results)
    
    paramValueTable = pd.DataFrame.from_dict(results['BEAAPI']['Results']['ParamValue'])

    return paramValueTable

def getParameterValuesFiltered(dataSetName: str, targetParameter: str, tableName: str) -> pd.DataFrame:
    """GetParameterValuesFiltered - retrieves a list of the valid values for a particular parameter
    based on other provided parameters.

    Input
    ----------------------------------
    dataSetName: str, example "Regional"

    targetParameter: str, example "LineCode"

    tableName: str, example "SAINC1"

    Returns
    ------------------------------------
    values for one target parameter based on the values of the other named parameters.
    """

    global user_ID

    method = "GETPARAMETERVALUESFILTERED"

    url = f"https://apps.bea.gov/api/data?&UserID={user_ID}" \
                f"&method={method}&" \
                f"&datasetname={dataSetName}" \
                f"&TargetParameter={targetParameter}" \
                f"&TableName={tableName}" \
                "&ResultFormat=JSON"
    results = json.loads(getResult(url).content)

    _checkForError(results)

    filteredParamValues = results['BEAAPI']['Results']['ParamValue']
    
    filteredParamValueTable = pd.DataFrame.from_dict(results['BEAAPI']['Results']['ParamValue'])

    return filteredParamValueTable

def getData(dataSetName: str, **kwargs):
    
    """
        Retrieves data from BEA

        Required Parameters: DatasetName, additional required parameters (depending on the
        dataset)

        Optional Parameters: additional optional parameters (depending on the dataset)
        
        Result: Dimensions nodes with attributes:

            • Ordinal – ordinal number indicating a standardized order of returned dimensions – note that attributes in
            returned data are not guaranteed to be in any particular order. Programmatic usage of attributes should
            refer to them by name.
            • Name – The Name of each data dimension returned
            • DataType – string or numeric – whether the data dimension is purely numeric or should be treated as
            string data

        • IsValue – most datasets have one dimension that represents the statistic of interest, and the other
        dimensions are descriptive of the statistic. IsValue = 1 for the data dimension that is the statistic
        of interest, otherwise 0. The statistic of interest is usually numeric so that it can be summarized or
        aggregated based on the descriptive dimension values.

        Each Dataset contains different dimensions. There are a few pre-defined dimensions that are common to most
        Datasets, including:
            • CL_UNIT – a descriptor of the units reported for the data value (e. g. USD for U. S. dollars, and PC
        for percent)
            • UNIT_MULT – a descriptor of the multiplier that applies to the data value. This value is the base-
        10 exponent that should be applied to the data value (e. g. amounts reported in millions would have
        a UNIT_MULT of 6; amounts reported in billions would have a UNIT_MULT of 9).

        The specific meaning of each dimension is described in the Appendix for each dataset.
        
        The result then includes Data nodes containing the actual results specified in the parameters. Each Data
        node contains one attribute for each data dimension (specified in the Dimensions nodes).

        Finally, the result may include Note nodes. Notes (as in footnotes) further describe or qualify any of the other
        nodes in the result (or the result node itself). A result node qualified by a Note has an attribute named
        NoteRef. If a result node includes the NoteRef attribute, the value for it will always be present among the
        Notes nodes.

        Example:
        https://apps.bea.gov/api/data/?&UserID=Your-36Character-Key&method=GetData&datasetname=Regional&TableName=CAINC1&LineCode=3&GeoFIPS=DE&Year=2014&ResultFormat=XML
    """

    specified_additonal_options = ""

    for key, value in kwargs.items():
        specified_additonal_options += f"&{key}={value}"

    method = "GetData"

    global user_ID
    url = f"https://apps.bea.gov/api/data?&UserID={user_ID}" \
                f"&method={method}&" \
                f"&datasetname={dataSetName}" \
                "&ResultFormat=JSON" + specified_additonal_options
                
    
    results = json.loads(getResult(url).content)

    _checkForError(results)
    
    # dimensions are columns, datavalues are rows, notes are notes
    
    try:
        data = pd.DataFrame.from_dict(results['BEAAPI']['Results'].get('Data'))
        notes = pd.DataFrame.from_dict(results['BEAAPI']['Results'].get('Notes'))
        columns = pd.DataFrame.from_dict(results['BEAAPI']['Results'].get('Dimensions'))
    
    except:
        print(pprint.pformat(results,indent=4))

    return data, notes, columns 

def getResult(url):
    request = requests.get(url, verify=False)
    return request

