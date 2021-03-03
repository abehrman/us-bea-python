import pytest
import sys

sys.path.append("./")

import bea

def test_getParameterListForRegional():
    result = bea.getParameterList('Regional')

    assert result is not None
    
def test_getDataSetList():
    result = bea.getDataSetList()

    assert result is not None

def test_getParameterList():
    result= bea.getParameterList('Regional')

    assert result is not None

def test_getParameterValues():
    result = bea.getParameterValues("IntlServTrade", "TradeDirection")

    assert result is not None

def test_getParameterValuesFiltered():
    result = bea.getParameterValuesFiltered("Regional", "LineCode", "SAINC1")

    assert result is not None

def test_getData():
    result = bea.getData("Regional", tablename="CAINC1", linecode="3", geoFIPS="DE", year="2014")

    assert result is not None
