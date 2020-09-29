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

messageAlert = ["--error",
                "--Green... All OK",
                "--Amber... Time to make a list of essentials...",
                "--Amber... Go and buy essentials...",
                "--Red... Now PANIC..." ]

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
    if not num:
        message = messageAlert[0]
    else:
        num = int(num[3])
        if num >= 0 and num <=9:
            message = messageAlert[1]
        elif num >=10 and num <=15:
            message = messageAlert[2]
        elif num >15 and num <=20:
            message = messageAlert[3]
        elif num >20:
            message = messageAlert[4]
        else:
            message = messageAlert[0]
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
        message = messageUpdate(numOfCases)
        print(message, response.content.decode()[60:])

if __name__ == "__main__":
    main()
 