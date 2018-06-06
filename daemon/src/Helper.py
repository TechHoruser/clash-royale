import logging
import os
import datetime

from itertools import islice
from daemon.src.Params import Params
from daemon.src.DB import DB


class Helper(object):
    def __init__(self):
        self.db = DB()

    def chunks(self, data, SIZE=Params.chunkSize):
        it = iter(data)
        for i in range(0, len(data), SIZE):
            yield {k: data[k] for k in islice(it, SIZE)}

    def battleInClan(self, battle, player_tag):
        for player in battle['team']:
            if player['tag'] == player_tag:
                try:  # Puede ser que el usuario no estuviese en ningún clan
                    return player['clan']['tag'] == Params.clanCode
                except TypeError:
                    return False

    def addClanWar(self, clan_war_data):
        if not self.db.clanWarIsSaved(clan_war_data[0]):
            # TODO: Actualizar puntuaciones de jugadores
            self.db.addClanWar(clan_war_data[0])

    def proccessBattlesOfPlayer(self, player_name, player_tag, battles):
        new_battles = 0

        # for battle in battles[::-1]:
        for battle in battles:

            battle['player'] = {
                'name': player_name,
                'tag': player_tag
            }

            '''
            Si la batalla en orden por fecha descendente se encuentra almacenada
            ya tenemos almacenadas el resto de batallas o que el combate no se produzca en el clan
            '''
            if self.db.battleIsSaved(battle) or not self.battleInClan(battle, player_tag):
                break

            new_battles += 1

            '''
            Guarda la batalla en Mongo
            '''
            self.db.addBattle(battle)

            if battle['type'] in Params.clan_battles_type:
                self.db.addBattleOfClan({
                    'player': battle['player'],
                    'utcTime': battle['utcTime'],
                    'deck': Helper.getThePlayerData(battle)['deckLink'],
                    'type': battle['type'],
                    'teamCrowns': battle['teamCrowns'],
                    'opponentCrowns': battle['opponentCrowns']
                })



        if new_battles > 0:
            logging.info(
                'Jugador "' + player_name + '#' + player_tag + '"' +
                ' ha realizado ' + str(new_battles) + ' nueva' + ('s' if new_battles > 1 else '')+' batallas'
            )

    @staticmethod
    def getFilesError():
        files = []

        for (dirpath, dirnames, filenames) in os.walk(Params.project_path+'/errors'):
            filenames.remove('.empty')

            for filename in filenames:
                files.append({
                    'name': filename,
                    'fullpath': Params.project_path+'/errors/'+filename,
                    'timestamp': os.path.getmtime(Params.project_path+'/errors/' + filename)
                })

        return files

    @staticmethod
    def removeOldErrors():
        # Mínimo momento donde persistirá el fichero
        datetime_limit = datetime.datetime.now() - datetime.timedelta(hours=Params.file_duration_hours)
        for file in Helper.getFilesError():
            # Mínimo del fichero
            datetim_file = datetime.datetime.fromtimestamp(file['timestamp'])

            if datetim_file < datetime_limit:
                logging.info('Eliminado fichero error: '+file['name'])
                os.remove(file['fullpath'])

    @staticmethod
    def getThePlayerData(battle):
        if len(battle['team']) == 1 or battle['team'][0]['tag'] == battle['player']['tag']:
            return battle['team'][0]

        return battle['team'][1]


class Printer:
    @staticmethod
    def printSeparator(msg=''):
        if msg == '':
            logging.info(Params.separator_char * Params.separator_tam )

        else:
            number_seps = Params.separator_tam - len(msg) - 2

            logging.info(
                str(Params.separator_char * int(number_seps / 2)) +
                ' ' + msg + ' ' +
                str(Params.separator_char * int(number_seps / 2)) +
                Params.separator_char if not isinstance((number_seps / 2), int) else ''
            )

    @staticmethod
    def printInRectangle(msg):
        Printer.printSeparator()
        Printer.printSeparator(msg)
        Printer.printSeparator()

    @staticmethod
    def printBetweenLines(msg):
        Printer.printSeparator()
        logging.info(msg)
        Printer.printSeparator()
