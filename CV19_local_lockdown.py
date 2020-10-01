import os
import re
from requests import get
from json import dumps
import xml.etree.ElementTree as ET

configFileName = "cvConfig.xml"

# Load settings data from the cvConfig.xml 
def loadSettings(file_path):
    cvConfigFiletree = ET.parse(file_path)
    cvConfigFileroot = cvConfigFiletree.getroot()
    ENDPOINT = cvConfigFileroot[0][0].text
    caseNumposition = int(cvConfigFileroot[0][1].text)
    dataNumPosition = int(cvConfigFileroot[0][2].text)
    HEADER = [cvConfigFileroot[0][3].text]
    AREA_TYPE = cvConfigFileroot[0][4].text
    AREA_NAME = []

    for area in cvConfigFileroot.iter('localArea'):
        t = area.text
        AREA_NAME.append(t)
    return caseNumposition,dataNumPosition,HEADER,AREA_TYPE,AREA_NAME,ENDPOINT



# Format (low threshold, high threshold, message)
# Message is seleced if low_threshold <= num < high_threshold
messageOutAlert = [ (0, 10, "--Green... All OK"),
                 (10, 15, "--Amber... Time to make a list of essentials..."),
                 (15, 20, "--Amber... Go and buy essentials..."),
                 (20, 99999, "--Red... Now PANIC...") ]

# Build response string.
def buildResponse(a_name,AREA_TYPE,ENDPOINT):
    filters = [
    f"areaType={AREA_TYPE}",
    f"areaName={a_name}"
    ]

    structure = {
    "date": "date",
    "name": "areaName",
    "dailyCases": "newCasesByPublishDate",
    "newDeaths": "newDeaths28DaysByPublishDate",
    "cumDeaths28DaysByPublishDate":"cumDeaths28DaysByPublishDate",
    }

    api_params = {
    "format": "csv",
    "filters": str.join(";", filters),
    "structure": dumps(structure, separators=(",", ":")),
    "latestBy": "cumCasesByPublishDate"
    }
    return get(ENDPOINT, params=api_params, timeout=10)

# Output Header.
def printHeader(HEADER):
    print(HEADER)

# Output messages.
def messageUpdate(num):
    try:
        message = [m for m in messageOutAlert if m[0]<=num and num<m[1]][0]
    except TypeError:
        message = f"messageUpdate was given '{num}' but expected a number"
    except IndexError:
        message = f"messageUpdate was given an invalid index of {num}"
    return message 

# Find the number of cases in each location.
def getNumOfCases(response):
    numOfCases = re.findall(r'\b\d+\b',response.content.decode()[30:])
    if numOfCases == True:
        numOfCases = [int(i) for i in numOfCases]
        #message = messageUpdate(num)
    return numOfCases

# Get the file path to the config.xml file.
def getFilePath():
    cwd_path = os.path.abspath(__file__)
    path_list = cwd_path.split(os.sep)
    script_directory = path_list[0:len(path_list)-1]
    file_path = "\\".join(script_directory)+"\\"+ configFileName
    return file_path

# Main program. 
def main():
    file_path = getFilePath()
    caseNumposition,dataNumPosition,HEADER,AREA_TYPE,AREA_NAME, ENDPOINT = loadSettings(file_path)
    printHeader(HEADER)
    for a_name in AREA_NAME:
        response = buildResponse(a_name,AREA_TYPE,ENDPOINT)
        try:
            assert response.status_code == 200
        except AssertionError as error:
            f"Failed request: {response.text}"
        print(messageUpdate(int(getNumOfCases(response)[caseNumposition])), response.content.decode()[dataNumPosition:])
    
if __name__ == "__main__":
    main()
 