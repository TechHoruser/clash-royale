import requests
import datetime

from daemon.src.Params import Params


class ApiConnector:
    @staticmethod
    def sendRequest(url):
        headers = {'auth': Params.token}
        response = requests.request("GET", url, headers=headers)

        if response.status_code == 200:
            return response.json()

        raise ApiConnectorException(response.status_code, response.text)

    @staticmethod
    def getBattles(tags):
        url = Params.endPoint+'/player/'+tags+'/battles'

        return ApiConnector.sendRequest(url)

    @staticmethod
    def getClanData():
        url = Params.endPoint+'/clan/'+Params.clanCode

        return ApiConnector.sendRequest(url)

    @staticmethod
    def getPetitions():
        url = Params.endPoint+'/auth/stats'

        return ApiConnector.sendRequest(url)

    @staticmethod
    def getClanWar():
        url = Params.endPoint+'/clan/'+Params.clanCode+'/war'

        return ApiConnector.sendRequest(url)

    @staticmethod
    def getClanWarLog():
        url = Params.endPoint+'/clan/'+Params.clanCode+'/warlog'

        return ApiConnector.sendRequest(url)


class ApiConnectorException(Exception):
    def __init__(self, http_code, content):
        filename = 'error-'+str(datetime.datetime.now())+'.html'
        with open(Params.project_path+'/errors/'+filename, 'w') as file:
            file.write(content)

        self.errors = 'Error al conectar a royaleapi.com (HTTP CODE: '+str(http_code)+') '+\
                      '['+filename+']'
