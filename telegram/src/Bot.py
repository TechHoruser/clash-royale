# !/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram.src.Params import Params
from telegram.src.DB import DB

import telebot
import threading
import time
import datetime
import logging.handlers

logger = logging.getLogger('bot-request')
logger.setLevel(logging.DEBUG)
handler = logging.handlers.TimedRotatingFileHandler(filename=Params.project_path + '/logs/requests.log', when="d", interval=1, backupCount=5)
formatter = logging.Formatter(fmt='(%(asctime)s - %(levelname)s):\n%(message)s\n------', datefmt='%d/%m/%y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)

tb = telebot.TeleBot(Params.token)

'''
List of Commands:
start - Bienvenido al cala
rules - Reglas del clan
get_id - Devuelve el id de tu usuario
previous_war - Datos de la última gerra jugada
my_score - Te muestra los puntos que tienes actualmente
scores - Muestra las puntuaciones de los miembros
active_notifications - Activa las notificaciones que tengas disponibles
help - Envia un mensaje al administrador
get_log - Solo Creador, para revisar posibles errores
'''

db = DB()

emoji_point = '\U000026AA'
exclamation = '\U000026A0'

welcome_text = 'Bienvenido al bot para la gestión del clan.\n' \
               'En primer lugar mostrar las reglas (/rules) y como evolucionarás en base a puntos.'

rules_text = exclamation + '*Normas*' + exclamation + '\n\n' \
             'Adquisión de puntos:\n' \
             '  *+1* : Guerra de clan jugada\n' \
             '  *+2* : Guerra de clan ganada\n\n' \
             'Pérdida de puntos:\n' \
             '  *-10*: Guerra de clan no jugada (Habiendo jugado la recolección)\n\n' \
             'Rol según puntuación (p):\n' \
             ' *p < 0*:                 Expulsión\n' \
             ' *0 <= p < 15*:      Miembro\n' \
             ' *15 <= p < 100*:  Veterano\n' \
             ' *100 <= p*:          Coolider'

#TODO: +1: Por cada 200 donaciones el domingo a las 11
#TODO: -10: Menos de 200 donaciones

help_msg = '*EN DESARROLLO*\n\n' + emoji_point + ' Guardado de puntuación personal\n\n' \
           'En caso de querer enviar una propuesta al creador escribir:\n' \
            '_/help "mensaje"_\n\n' \
           '*Muchas Gracias*'


def print_log(message):
    msg = 'Usuario: ' + (
        '' if message.from_user.username is None else message.from_user.username) + '(' + str(
        message.from_user.id) + ')\n'
    msg += 'Texto: ' + message.text + '\n'
    logger.info(msg)


@tb.message_handler(commands=['start'])
def welcome(message):
    print_log(message)
    tb.send_message(message.chat.id, welcome_text)
    tb.send_message(message.chat.id, rules_text, parse_mode='Markdown')


@tb.message_handler(commands=['rules'])
def rules(message):
    print_log(message)
    tb.send_message(message.chat.id, rules_text, parse_mode='Markdown')


@tb.message_handler(commands=['previous_war'])
def previous_war(message):
    print_log(message)
    previus_war = db.getPreviusWar()
    date = datetime.datetime.fromtimestamp(
        int(previus_war['createdDate'])
    ).strftime('%d/%m/%Y %H:%M:%S')
    msg = 'Guerra finalizada el ' + date
    msg += '\nPuesto (' + str(get_position_in_war(previus_war)) + ')\n'
    for participant in previus_war['participants']:
        msg += '\n'

        # TODO: Pendiente de ver batallas disponibles (dependencia de royaleapi)
        if participant['battlesPlayed'] >= 1 and participant['wins'] >= 1:
            msg += '+3  '
        elif participant['battlesPlayed'] == 1 and participant['wins'] == 0:
            msg += '+1  '
        elif participant['battlesPlayed'] == 0:
            msg += '-10  '

        msg += participant['name'] + '#' + participant['tag']

    tb.send_message(message.chat.id, msg)


@tb.message_handler(commands=['get_id'])
def get_id(message):
    print_log(message)
    tb.send_message(message.chat.id, 'Su id es: *'+str(message.chat.id)+'*', parse_mode='Markdown')


@tb.message_handler(commands=['my_score'])
def my_score(message):
    print_log(message)
    building(message.chat.id)


@tb.message_handler(commands=['scores'])
def scores(message):
    print_log(message)
    building(message.chat.id)


@tb.message_handler(commands=['active_notifications'])
def active_notifications(message):
    print_log(message)
    building(message.chat.id)


@tb.message_handler(commands=['get_log'])
def get_log(message):
    if message.chat.id == Params.owner_id:
        tb.send_document(Params.owner_id, open(Params.project_path+'/logs/requests.log', 'rb'))
    else:
        tb.send_message(message.chat.id, 'No tiene permisos')


@tb.message_handler(commands=['help'])
def get_id(message):
    print_log(message)
    chat_text = message.text.split(" ", 1)
    if len(chat_text) == 1:
        tb.send_message(
            message.chat.id,
            help_msg,
            parse_mode='Markdown'
        )
    else:
        # TODO: Pintado de botones para ver si el comentario es aceptado o puede llevar algún report o ban (inlineQuery)

        tb.send_message(
            Params.owner_id,
            'Usuario ' +
            ('' if message.from_user.username is None else message.from_user.username) +
            ' con id *' +
            str(message.chat.id) +
            '*, dice:\n' +
            chat_text[1],
            parse_mode='Markdown'
        )

        tb.send_message(message.chat.id, '\U00002714 Mensaje enviado correctamente')


@tb.message_handler()
def not_found(message):
    print_log(message)
    tb.send_message(message.chat.id, 'Comando no reconocido')


def building(chat_id):
    tb.send_sticker(chat_id, open(Params.project_path+'/data/building.png', 'rb'))


def get_position_in_war(clan_war):
    for pos, clan in enumerate(clan_war['standings']):
        if clan['tag'] == Params.clanCode:
            return int(pos)+1
    return 0


def notify_server_on():
    try:
        tb.send_message(Params.owner_id, 'Servidor Arrancado')
    except telebot.apihelper.ApiException:
        logger.info('El propietario (' + str(Params.owner_id) + ') tiene bloqueado el bot')


def notify_admins():
    while True:
        for admin in Params.admins:
            '''En caso de tener el Bot bloqueado lanzará una excepción'''
            try:
                # TODO: Pendiente de notificar
                '''
                    fin de guerra
                    puntuaciones
                    degradaciones/ascensos
                '''
                tb.send_message(admin['id'], 'Notificación a administrador')

            except telebot.apihelper.ApiException:
                logger.info('Administrador \''+admin['username']+'\' ('+str(admin['id'])+') tiene bloqueado el bot')

        # TODO: Calcular sleep hasta fin de la guerra
        time.sleep(10)


time.sleep(1)

notify_server_on()

threads = list()
t = threading.Thread(target=notify_admins)

# t.start()

tb.polling(none_stop=True)
