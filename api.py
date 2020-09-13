# coding: utf-8
# Импортирует поддержку UTF-8.
from __future__ import unicode_literals

# Импортируем модули для работы с JSON и логами.
import json
import logging
import pandas as pd
import random

# Импортируем подмодули Flask для запуска веб-сервиса.
from flask import Flask, request
app = Flask(__name__)


logging.basicConfig(level=logging.DEBUG)

# Хранилище данных о сессиях.
sessionStorage = {}
df = pd.read_json(r'date.json',encoding='utf8')

# Задаем параметры приложения Flask.
@app.route("/", methods=['POST'])

def main():
# Функция получает тело запроса и возвращает ответ.
    logging.info('Request: %r', request.json)

    response = {
        "version": request.json['version'],
        "session": request.json['session'],
        "response": {
            "end_session": False
        }
    }

    handle_dialog(request.json, response)

    logging.info('Response: %r', response)

    return json.dumps(
        response,
        ensure_ascii=False,
        indent=2
    )

# Функция для непосредственной обработки диалога.
def handle_dialog(req, res):
    user_id = req['session']['user_id']

    if req['session']['new']:
        # Это новый пользователь.
        # Инициализируем сессию и поприветствуем его.

        sessionStorage[user_id] = {
            'suggests': [
                "Пособие на детей до 3х лет",
                "Пособие для детей в неполных семьях",
                "выплата на первого ребенка",
            ]
        }

        res['response']['text'] = 'Привет! Я помогу подобрать перечень документов. Просто назовите льготу, выплату или пособие, которое хотите получить?'
        res['response']['buttons'] = get_suggests(user_id)
        return
    answer = req['request']['original_utterance'].lower()
    result = df[df["full_name"].str.contains(answer)]
    if len(result) ==1:
        res['response']['text'] = 'Вам необходимо собрать следующие документы: ' + ', '.join(result.voice_docs.values[0])
        return
    if len(result) >1:
        res['response']['text'] = 'Я нашла '+str(len(result)) +' документа: \n'+', '.join(result["full_name"].values) +'. Уточните, пожалуйста, что вас интересует?'
        return    
    if  answer in ['помощь','что ты умеешь','что ты умеешь?']:
        res['response']['text'] = 'Я рассказываю о льготах, выплатах и документах, которые нужны, чтобы их получить'
        return
    if  answer in ['спасибо','спасибо, алиса']:
        res['response']['text'] = random.choice(['Обращайтесь','Была рада помочь','Не за что!', 'Пожалуйста! Приходите ещё.'])
        return
    # Если ответ не распознан  переспрашиваем
    res['response']['text'] = random.choice(['Извините, я не поняла','Повторите, пожалуйста!','Кажется, я вас не понимаю!', 'Такой ответ мой разработчик не предусмотрел']) 
    res['response']['buttons'] = get_suggests(user_id)

# Функция возвращает две подсказки для ответа.
def get_suggests(user_id):
    session = sessionStorage[user_id]

    # Выбираем две первые подсказки из массива.
    suggests = [
        {'title': suggest, 'hide': True}
        for suggest in session['suggests'][:2]
    ]

    # Убираем первую подсказку, чтобы подсказки менялись каждый раз.
    session['suggests'] = session['suggests'][1:]
    sessionStorage[user_id] = session

    # Если осталась только одна подсказка, предлагаем подсказку
    # со ссылкой на Яндекс.Маркет.
    if len(suggests) < 2:
        suggests.append({
            "title": "Ладно",
            "url": "https://market.yandex.ru/search?text=художники",
            "hide": True
        })

    return suggests
