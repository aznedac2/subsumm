# -*- coding: utf-8 -*-
from flask import Flask, render_template, request

import datetime

from gensim.summarization.summarizer import summarize
import re
import xml.etree.ElementTree as ET
import urllib.request, urllib.parse, urllib.error
from bs4 import BeautifulSoup
import ssl
import json
import requests

app = Flask(__name__)

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')
    if request.method == 'POST':
        # 파라미터를 전달 받습니다.
        raw_url = request.form['raw_url']
        a, b = raw_url.split('?v=')

        src_url = 'https://www.youtube.com/embed/' + b
        url = 'http://video.google.com/timedtext?lang=en&v=' + b
        xml = urllib.request.urlopen(url, context=ctx).read()

        tree = ET.fromstring(xml)

        # 빈 단어 리스트를 선언합니다.
        words = []

        for line in tree:
          line = line.text.strip()
          word = line.split()
          words = words + word

        string = " ".join(words)
        string = string.replace("&#39;","'")
        string = string.replace("&quot;",'"')

        fullwords = string.split(' ')

        text = summarize(string, word_count=50)
        # text = summarize(string, ratio=0.1)
        fulltext = summarize(string, ratio=1.0)

        # 네이버 파파고 api이용하기
        tr_url="https://openapi.naver.com/v1/papago/n2mt?source=en&target=ko&text="
         
        request_url = "https://openapi.naver.com/v1/papago/n2mt"
        headers= {"X-Naver-Client-Id": "E3Qm4KfmUlFJjFRsCuTf", "X-Naver-Client-Secret":"Qbj4Gdlgi2"}
        params = {"source": "en", "target": "ko", "text": text}
        response = requests.post(request_url, headers=headers, data=params)
        # print(response.text)
        result = response.json()
        if 'errorMessage' in result:
          trtext = '요약 번역 쿼리 한도를 초과했습니다'
        else:
          trtext = result['message']['result']['translatedText']

        return render_template('index.html', src_url=src_url, text=text, fulltext = fulltext, trtext = trtext)

if __name__ == '__main__':
   app.run(debug = True)