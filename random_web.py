import flask
import random

word_cnt = 20

with open('words.txt', 'r') as infile:
    words = infile.readlines()


header = """<!DOCTYPE html>
<html>
<head>
<title>Word Nerd Tool</title>
<style>
body {
  font-family: roboto;
  font-family: tahoma;
  font-family: arial;
}
a {
  color: black;
  text-decoration: none;
}
</style>
<body>
<h1>&nbsp;&nbsp;<a href="javascript:history.go(0)">REFRESH</A></h1><h2>
"""    
   

app = flask.Flask('random english words')


@app.route('/', methods=['GET'])
def home():
    random.seed()
    html = header
    for i in range(word_cnt):
        word = random.choice(words).strip()
        html += '&nbsp;&nbsp;&nbsp;&nbsp;<a href="https://www.google.com/search?q=%s+definition" target="_new">%s</a><br>' % (word, word)
    html += '</h2></body></html>'
    return flask.Response(html, mimetype='text/html')


if __name__ == '__main__':
    print('go to http://localhost or http://127.0.0.1')
    app.run(host='0.0.0.0', port=80)