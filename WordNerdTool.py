import flask
from flask import request
import json
import nltk
from nltk.corpus import wordnet as wn

print('loading wordnet...')
nltk.download('wordnet')

print('loading all synsets')
all_synsets = list(wn.all_synsets())



base_html = """
<html>
<head>
<title>Word Nerd Tool</title>
<style>
* {font-family: Calibri;}
a {color: #d5000d;}
table {border-width: 1px; border-style: solid; border-color: lightgray; border-collapse: collapse; white-space: nowrap;}    
th {border-width: 1px; padding: 4px; border-style: solid; border-color: lightgray; background-color: lightskyblue; white-space: nowrap;}
td {border-width: 1px; padding: 4px; border-style: solid; border-color: lightgray; white-space: nowrap;}
.flex-container {display: flex; flex-wrap: wrap; background-color: LightGray;}
.flex-container > div {margin: 10px; background-color: White; padding: 10px}
tr:nth-child(even) {background-color: #E7F5FE;}
h2 {color: #d5000d;
    font-size: 28px;
    font-weight: bold;}
h1 {color: #000dd5;
    font-size: 32px;
    font-weight: bold;}
</style>
</head>
<body>
<div class="flex-container">
<div>
<h1>Search</h1>
<form action="/search" method="post">
<label for="search">Search term:</label><br>
<input type="text" placeholder="Search Term" name="search" id="search" size="50"><br>

<label for="definition">Search definitions:</label>
<input type="checkbox" id="definition" name="definition" value="definition"><br>

<label for="prefix">Prefix:</label><br>
<input type="text" placeholder="Prefix" name="prefix" id="prefix" size="20"><br>

<label for="suffix">Suffix:</label><br>
<input type="text" placeholder="Suffix" name="suffix" id="suffix" size="20"><br>

<input type="radio" id="all" name="pos" value="all" checked>
<label for="noun">All POS</label><br>

<input type="radio" id="noun" name="pos" value="noun">
<label for="noun">Nouns</label><br>

<input type="radio" id="verb" name="pos" value="verb">
<label for="verb">Verbs</label><br>

<input type="radio" id="adjective" name="pos" value="adjective">
<label for="adjective">Adjectives</label><br>

<input type="radio" id="adverb" name="pos" value="adverb">
<label for="adverb">Adverbs</label><br>

<button type="submit">Submit</button>
</form>
</div>
"""


def expand_synset(synset):
    html = '<hr><h2><a href="/wordnet/%s">%s</a></h2>' % (synset.name(), synset.name())
    pos = synset.pos()
    # part of speech
    if pos == 'n':
        html += '<p><b>POS:</b> <i>noun</i><br>'
    elif pos == 'a':
        html += '<p><b>POS:</b> <i>adjective</i><br>'
    elif pos == 'v':
        html += '<p><b>POS:</b> <i>verb</i><br>'
    elif pos == 's':
        html += '<p><b>POS:</b> <i>adjective satellite</i><br>'
    elif pos == 'r':
        html += '<p><b>POS:</b> <i>adverb</i><br>'
    else:
        html += '<p><b>POS:</b> <i>%s</i><br>' % pos
    # definition
    html += '<b>Definition:</b> %s<br>' % synset.definition()
    # examples
    html += '<b>Examples:</b><br><ul>'
    for example in synset.examples():
        html += '<li>%s</li>' % example
    html += '</ul>'
    # lemmas
    html += '<b>Lemmas:</b><br><ul>'
    for lemma in synset.lemma_names():
        html += '<li>%s</li>' % lemma
    html += '</ul>'
    # antonyms
    html += '<b>Antonyms:</b><br><ul>'
    for lemma in synset.lemmas():
        for antonym in lemma.antonyms():
            html += '<li>%s</li>' % antonym.name()
    html += '</ul>'
    #close
    html += '</p>'
    return html


def compile_from_definition(search):
    results = list()
    terms = search.split(' ')
    for synset in all_synsets:
        d = str(synset.definition())
        if search in d:
            results.append(synset)
            continue
        match = True
        for term in terms:
            if term not in d:
                match = False
                break
        if match:
            results.append(synset)
        # TODO add squishy definition search
    return results

app = flask.Flask('WordNerdTool')


@app.route('/', methods=['get'])
def home():
    return base_html


@app.route('/search', methods=['get','post'])
def search():
    if request.method == 'POST':
        html = base_html
        fields = ['search', 'definition', 'prefix', 'suffix', 'pos']
        form = dict()
        for field in fields:
            data = request.form.get(field, '')
            form[field] = data
        print(form)
        html += '<div><h1>Results</h1>'
        
        # for normal word search
        if form['definition'] == '':
            synsets = wn.synsets(form['search'])
        elif form['definition'] == 'definition':
            synsets = compile_from_definition(form['search'])

        # filter POS
        if form['pos'] == 'noun':
            synsets = [i for i in synsets if i.pos() == 'n']
        if form['pos'] == 'verb':
            synsets = [i for i in synsets if i.pos() == 'v']
        if form['pos'] == 'adjective':
            synsets = [i for i in synsets if i.pos() == 'a' or i.pos() == 's']
        if form['pos'] == 'adverb':
            synsets = [i for i in synsets if i.pos() == 'r']

        # filter prefix/suffix
        if form['prefix'] != '':
            synsets = [i for i in synsets if i.name().startswith(form['prefix'])]
        if form['suffix'] != '':
            synsets = [i for i in synsets if i.name().split('.')[0].endswith(form['suffix'])]

        for synset in synsets:
            html += expand_synset(synset)
        html += '</div></body></html>'
        return html
    

@app.route('/wordnet/<term>', methods=['get'])
def wordnet(term):
    html = base_html
    base_synset = wn.synset(term)
    # base word div
    html += '<div><h1>Base Word</h1>'
    html += expand_synset(base_synset)
    # TODO add antonyms, root hypernyms
    html += '</div>'
    # hyponyms
    html += '<div><h1>Hyponyms</h1>'
    for synset in base_synset.hyponyms():
        html += expand_synset(synset)
    html += '</div>'
    # hypernyms
    html += '<div><h1>Hypernyms</h1>'
    for synset in base_synset.root_hypernyms():
        html += expand_synset(synset)
    for synset in base_synset.hypernyms():
        html += expand_synset(synset)
    html += '</div>'
    # holonyms
    html += '<div><h1>Holonyms</h1>'
    for synset in base_synset.member_holonyms():
        html += expand_synset(synset)
    for synset in base_synset.part_holonyms():
        html += expand_synset(synset)
    for synset in base_synset.substance_holonyms():
        html += expand_synset(synset)
    html += '</div>'
    # meronyms
    html += '<div><h1>Meronyms</h1>'
    for synset in base_synset.member_meronyms():
        html += expand_synset(synset)
    for synset in base_synset.part_meronyms():
        html += expand_synset(synset)
    for synset in base_synset.substance_meronyms():
        html += expand_synset(synset)
    html += '</div>'
    
    # close and return
    html += '</div></body></html>'
    return html


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)