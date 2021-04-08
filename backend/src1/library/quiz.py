import re
import random
from flask import Flask
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, TemplateSendMessage, TemplateSendMessage, ButtonsTemplate, URIAction, PostbackAction, MessageAction
)
import requests
import urllib

app = Flask(__name__)


def make_quiz_button_template():
    select_option_num = 3
    # ボタンに入れられる文字が40文字まで
    title_limit = 20
    while True:
        wiki_title = get_random_title()
        if title_limit < len(wiki_title):
            continue
        description = get_description(wiki_title)
        image_url = get_image_url(wiki_title)
        if description is not None:
            description = delete_target_word(
                delete_braket(description), wiki_title)
            break

    url = f"https://ja.wikipedia.org/wiki/{urllib.parse.quote(wiki_title)}"
    actions = [PostbackAction(
        label=f"{wiki_title}", data=f'正解！！\n{url}')]
    while len(actions) <= select_option_num:
        conterfactual_titile = get_random_title()
        if title_limit < len(conterfactual_titile):
            continue
        if conterfactual_titile != wiki_title:
            actions.append(PostbackAction(label=f"{conterfactual_titile}",
                                          data=f'不正解！！答えは「{wiki_title}」でした！\n{url}'))

    random.shuffle(actions)

    message = TextSendMessage(text=description)
    buttons_template_message = TemplateSendMessage(
        alt_text='Buttons template',
        template=ButtonsTemplate(
            thumbnail_image_url=image_url,
            title='wikipedia クイズ',
            text='さて，上は何の説明でしょう？',
            actions=actions
        )
    )
    return message, buttons_template_message


def get_random_title():
    S = requests.Session()
    URL = f"https://ja.wikipedia.org/w/api.php?action=query&list=random&format=json&rnnamespace=0&rnlimit=1"
    R = S.get(url=URL)
    DATA = R.json()
    return DATA['query']['random'][0]['title']


def get_wikipedia(title):
    S = requests.Session()
    URL = "https://ja.wikipedia.org/w/api.php"

    PARAMS = {
        "action": "query",
        "prop": "revisions",
        "titles":  title,
        "rvprop": "content",
        "format": "json"
    }

    # get関数によって情報を取得
    R = S.get(url=URL, params=PARAMS)
    DATA = R.json()
    # jsonから必要なデータの抽出
    CONTENT = DATA['query']['pages']
    return CONTENT
    # id = list(CONTENT.keys())[0]
    # title = CONTENT[id]["title"]
    # geo, image_url, description = parse_mediawiki(
    #     CONTENT[id]['revisions'][0]['*'])
    # description = description.replace(title, '<MASK>')
    # return title, geo, image_url, description


def get_description(title):
    S = requests.Session()
    URL = "https://ja.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&exintro&explaintext&redirects=1"
    PARAMS = {
        "titles": title
    }
    R = S.get(url=URL, params=PARAMS)
    DATA = R.json()
    try:
        pageid = list(DATA['query']['pages'].keys())[0]
        return DATA['query']['pages'][str(pageid)]['extract']
    except:
        return None


def get_geolocation(mw):
    geo = re.search(r'\|geo.*?\{\{(?P<geo>.*?)}}', mw)
    if geo is not None:
        return geo.group("geo")


# def get_pageid(title):
#     S = requests.Session()
#     URL = "https://ja.wikipedia.org/w/api.php"

#     PARAMS = {
#         "action": "query",
#         "format": "json",
#         "list": "search",
#         "srsearch": title
#     }

#     R = S.get(url=URL, params=PARAMS)
#     DATA = R.json()

#     for result in DATA['query']['search']:
#         if result['title'] == title:
#             return result["pageid"]


def get_image_url(title):
    S = requests.Session()
    URL = f'https://ja.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(title)}'
    R = S.get(url=URL)
    DATA = R.json()
    try:
        return DATA["thumbnail"]["source"]
    except:
        app.logger.warning("no image url")
        return "https://example.com"

# def delete_meta(mw):
#     mw = re.sub(r'<ref.*?>.*?</ref>', '', mw, flags=re.DOTALL)
#     mw = re.sub(r'<.*?>', '', mw, flags=re.DOTALL)
#     return mw


# def delete_file_and_category(mw):
#     mw = re.sub(
#         r'\[\[(?:ファイル:|File:|Category:)(?:[^\|{}\[\]]*?\|)*(.*?)\]\]', r'\1', mw)
#     return mw


# def delete_bullets(mw):
#     mw = re.sub(r'#REDIRECT', '', mw)
#     mw = re.sub(r'^[\#\*\;\:]+|----', '', mw, flags=re.MULTILINE)
#     return mw


# def delete_link(mw):
#     mw = re.sub(
#         r'\[\[(?!ファイル:|File:|Category:)(?:[^\|{}\[\]]*?\|)*(.*?)\]\]', r'\1', mw)
#     mw = re.sub(r'\{\{仮リンク\|([^\|]*)(?:\|[^\|]*?)*?\}\}', r'\1', mw)
#     mw = re.sub(
#         r'\[https?://[\w/:%#\$&\?\(\)~\.=\+\-]+ *?([^\ ]*?)\]', r'\1', mw)
#     mw = re.sub(r'https?://[\w/:%#\$&\?\(\)~\.=\+\-]+', '', mw)

#     return mw


# def delete_lang(mw):
#     mw = re.sub(r'\{\{lang(?:[^\|{}\[\]]*?\|)*(.*?)\}\}', r'\1', mw)

#     return mw


# def delete_template(mw):
#     mw = re.sub(r'\{\{.*?\}\}', '', mw)
#     return mw


def delete_braket(mw):
    mw = re.sub(r'[（(].*?[）)]', '', mw)
    return mw


def delete_target_word(mw, target):
    # 最初に空白を取り除く
    mw = mw.replace(' ', '')
    mw = mw.replace('　', '')
    return mw.replace(target, '<MASK>')

# def parse_mediawiki(mw):
#     app.logger.debug(mw)
#     geo = re.search(r'\|geo.*?\{\{(?P<geo>.*?)}}', mw, re.DOTALL)
#     image_url = re.search(r'\|image.*?=(?P<image>.*)', mw)
#     for line in mw.split('\n')[1:]:
#         if not line.startswith('|') and not line.startswith('{{'):
#             description = line
#             break
#     app.logger.debug(description)
#     func_list = [delete_link, delete_file_and_category, delete_lang,
#                  delete_meta, delete_bullets, delete_template, delete_braket]
#     for f in func_list:
#         description = f(description)

#     return geo.group("geo"), get_image_url(image_url.group('image')), description


# def get_image_url(text):
#     s = requests.Session()
#     url = "https://www.mediawiki.org/w/api.php"
#     params = {
#         "action": "query",
#         "format": "json",
#         "prop": "imageinfo",
#         "titles": "File:"+text,
#         "iiprop": "url"
#     }

#     r = s.get(url=url, params=params)
#     data = r.json()
#     im_url = data["query"]["pages"]["-1"]["imageinfo"][0]["url"]
#     return im_url
