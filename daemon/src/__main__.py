import time
import logging

from daemon.src.Helper import Helper, Printer
from daemon.src.ApiConector import ApiConnector, ApiConnectorException
from daemon.src.Params import Params

logging.basicConfig(filename=Params.project_path+'/logs/main.log', format='(%(asctime)s): %(message)s ', level=logging.INFO)

def externalProccessMemberOfClan():
    helper = Helper()

    clan_data = ApiConnector.getClanData()

    for member in clan_data['members']:

        logging.info('Procesando jugador ' + str(clan_data['members'].index(member) + 1) + '/' + str(len(clan_data['members'])))

        player_battles = ApiConnector.getBattles(member['tag'])

        helper.proccessBattlesOfPlayer(member['name'], member['tag'], player_battles)

        time.sleep(Params.sleep_miembros)

    number_petitions_per_day = ApiConnector.getPetitions()['requestCount']

    petitions_last_day = list(number_petitions_per_day.keys())[0]
    number_petitions_last_day = number_petitions_per_day[petitions_last_day]
    Printer.printBetweenLines('Día ' + petitions_last_day + ': ' + number_petitions_last_day)

def externalProccessClanWar():
    helper = Helper()

    helper.addClanWar(ApiConnector.getClanWarLog())


def internalProccess():
    Helper.removeOldErrors()


while True:
    Printer.printInRectangle('Nuevo Ciclo')

    try:
        # externalProccessMemberOfClan()
        externalProccessClanWar()
    except ApiConnectorException as e:
        Printer.printBetweenLines(e.errors)

    internalProccess()

    Printer.printInRectangle('Fin Ciclo')
    time.sleep(Params.sleep_general)

