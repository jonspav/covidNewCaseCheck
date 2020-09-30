import re
from requests import get
from json import dumps

ENDPOINT = "https://api.coronavirus.data.gov.uk/v1/data"
HEADER=["//// Covid-19 New Daily Cases  /////"]
AREA_TYPE = "ltla"
AREA_NAME = ["North Lincolnshire",
             "Doncaster",
             "East Hertfordshire",
             "North Hertfordshire",
             "Harlow","Broxbourne",
             "Welwyn Hatfield",
             "Milton Keynes"]

# Format is (low threshold, high threshold, message)
# Message is seleced if low_threshold <= num < high_threshold
messageAlert = [ (0, 10, "--Green... All OK"),
                 (10, 15, "--Amber... Time to make a list of essentials..."),
                 (15, 20, "--Amber... Go and buy essentials..."),
                 (20, 99999, "--Red... Now PANIC...") ]

# Build response string.
def buildResponse(a_name):
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
def printHeader():
    print(HEADER)

# Output messages.
def messageUpdate(num):
    try:
        message = [m for m in messageAlert if m[0]<=num and num<m[1]][0]
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

# Main program. 
def main():
    printHeader()
    for a_name in AREA_NAME:
        response = buildResponse(a_name)
        try:
            assert response.status_code == 200
        except AssertionError as error:
            f"Failed request: {response.text}"
        numOfCases = getNumOfCases(response)
        message = messageUpdate(int(numOfCases[3]))
        print(message, response.content.decode()[60:])

if __name__ == "__main__":
    main()
 