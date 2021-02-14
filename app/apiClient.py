#Provides functionality to perform requests on the ClinicalTrials.gov Api
import requests
from enum import Enum

#Usage
'''
- import it 
apiClient = ApiClient()

trials = apiClient.getTrialsFor(age = 29, sex = GenderEnum.male.value, isHealthy = HealthyVolunteersEnum.healthy.value) 

for trial in trials:
    print(trial.briefTitle)

#Trial object property: 
- NCTid
- briefTitle
- organization
- conditions (list of strings)
- locationState
- minimum age
- maximum age
- url (resolved with the NCTid)

'''

class GenderEnum(Enum):
    male = "Male"
    female = "Female"

class HealthyVolunteersEnum(Enum):
    healthy = "Accepts Healthy Volunteers"
    notHealthy = "No"

class ApiClient:

    #Returns a list of trials object
    def getTrialsFor(self, age: int, sex: GenderEnum, isHealthy: HealthyVolunteersEnum, max_trials = 100):

       

        params = {
            'expr' : f'prostate cancer AND AREA[HealthyVolunteers]"{isHealthy.value}" AND (AREA[Gender]"{sex.value}" OR Area[Gender]"All") AND SEARCH[Location](AREA[LocationCountry]United States AND AREA[LocationStatus]Recruiting)',
            'fmt' : 'JSON',
            'max_rnk': max_trials
        }

        jsonResponse = self.createRequest(params)
        trialsArray = []
        
        for study in jsonResponse['FullStudiesResponse']['FullStudies']:
            decodedStudy = self.decodeJSON(study)
            

            if self.isAgeMatching(age, int(decodedStudy.minimumAge), int(decodedStudy.maximumAge)):
                trialsArray.append(decodedStudy)
            

        return trialsArray
            
    #Run the request on the API with the specified parameters and returns a JSON file
    def createRequest(self, params):

        baseURL = "https://clinicaltrials.gov/api/query/full_studies?" #Check other available endpoints here https://clinicaltrials.gov/api/gui/ref/api_urls
        response = requests.get(baseURL, params = params)
        jsondata = response.json()

        return jsondata

    #Decode the Json and create the trial object
    def decodeJSON(self,study):

        NCTid = study['Study']['ProtocolSection']['IdentificationModule']['NCTId']
        briefTitle = study['Study']['ProtocolSection']['IdentificationModule']['BriefTitle']
        organization = study['Study']['ProtocolSection']['IdentificationModule']['Organization']['OrgFullName']
        conditions = study['Study']['ProtocolSection']['ConditionsModule']['ConditionList']['Condition']

        #get minimumAge
        try:
            if study['Study']['ProtocolSection']['EligibilityModule']['MinimumAge']:
                    minumumAge = study['Study']['ProtocolSection']['EligibilityModule']['MinimumAge'].rstrip('Years')                        
            else:
                minumumAge = "-1"
        except:
                minumumAge = "-1"

        #get maximumAge
        try:
            if study['Study']['ProtocolSection']['EligibilityModule']['MaximumAge']:
                    maximumAge = study['Study']['ProtocolSection']['EligibilityModule']['MaximumAge'].rstrip('Years')                        
            else:
                maximumAge = "101"
            
        except:
                maximumAge = "101"


        #Contact Details of Location
        try:
            if study['Study']['ProtocolSection']['ContactsLocationsModule']['LocationList']['Location']:
                locationState = study['Study']['ContactsLocationsModule']['LocationList']['Location'][0]['LocationState']
            else:
                locationState = "No data Available"

        except:
            locationState = "No data Available"

        trial = Trial(NCTid = NCTid, 
                briefTitle = briefTitle, 
                organization = organization, 
                conditions = conditions, 
                locationState = locationState,
                minimumAge = minumumAge,
                maximumAge = maximumAge
            )

        return trial
    
    #Check if the age inserted by the user is greater than minimum age 
    def isAgeMatching(self, age: int, minumumAge: int, maximumAge: int) -> bool:
        
        if age > minumumAge and age < maximumAge:
            return True
        else:
            return False
        

#Model
class Trial:

    def __init__(self, NCTid: str, briefTitle: str, organization, conditions: [str], locationState: str, minimumAge: int, maximumAge: int):
        self.NCTid = NCTid
        self.briefTitle = briefTitle
        self.conditions = conditions
        self.locationState = locationState
        self.url = f"https://clinicaltrials.gov/ct2/show/{NCTid}"
        self.minimumAge = minimumAge
        self.maximumAge = maximumAge

if __name__ == "__main__":

    apiClient = ApiClient()
    studies = apiClient.getTrialsFor(age = 35, sex = GenderEnum.male, isHealthy = HealthyVolunteersEnum.healthy)
    for study in studies:
        print(f"Minimum Age: {study.minimumAge} --- Maximum Age: {study.maximumAge}")