#!/usr/bin/env python
"""
wiktionary.py - jenni Wiktionary Module
Copyright 2009-2013, Michael Yanovich (yanovich.net)
Copyright 2009-2013, Sean B. Palmer (inamidst.com)
Licensed under the Eiffel Forum License 2.

More info:
 * jenni: https://github.com/myano/jenni/
 * Phenny: http://inamidst.com/phenny/
"""

import re
import web

uri = 'https://en.wiktionary.org/w/index.php?title=%s&printable=yes'
uri_ = 'https://en.wiktionary.org/wiki/%s'
r_tag = re.compile(r'<[^>]+>')
r_ul = re.compile(r'(?ims)<ul>.*?</ul>')

def text(html):
    text = r_tag.sub('', html).strip()
    text = text.replace('\n', ' ')
    text = text.replace('\r', '')
    text = text.replace('(intransitive', '(intr.')
    text = text.replace('(transitive', '(trans.')
    return text

def wiktionary(word):
    bytes = web.get(uri % web.urllib.quote(word.encode('utf-8')))
    bytes = r_ul.sub('', bytes)

    mode = None
    etymology = None
    definitions = {}
    for line in bytes.splitlines():
        if 'id="Etymology"' in line:
            mode = 'etymology'
        elif 'id="Noun"' in line:
            mode = 'noun'
        elif 'id="Verb"' in line:
            mode = 'verb'
        elif 'id="Adjective"' in line:
            mode = 'adjective'
        elif 'id="Adverb"' in line:
            mode = 'adverb'
        elif 'id="Initialism"' in line:
            mode = 'initialism'
        elif 'id="Interjection"' in line:
            mode = 'interjection'
        elif 'id="Particle"' in line:
            mode = 'particle'
        elif 'id="Preposition"' in line:
            mode = 'preposition'
        elif 'id="Prefix"' in line:
            mode = 'prefix'
        elif 'id="Suffix"' in line:
            mode = 'suffix'
        elif 'id="Proper_noun"' in line:
            mode = 'proper noun'
        elif 'id="Determiner"' in line:
            mode = 'determiner'
        elif 'id="Pronoun"' in line:
            mode = 'pronoun'
        elif 'id="Prepositional_phrase"' in line:
            mode = 'prepositional phrase'
        elif 'id="Conjunction"' in line:
            mode = 'conjunction'
        elif 'id="Abbreviation"' in line:
            mode = 'abbreviation'
        elif 'id="Numeral"' in line:
            mode = 'numeral'
        elif 'id="Phrase"' in line:
            mode = 'phrase'
        elif 'id="Symbol"' in line:
            mode = 'symbol'
        elif 'id="Participle"' in line:
            mode = 'participle'
        elif (mode == 'etmyology') and ('<p>' in line):
            etymology = text(line)

        if (mode is not None) and (('<li>' in line) or ('<li class="senseid"' in line)):
            definitions.setdefault(mode, []).append(text(line))

        if '<hr' in line:
            break
    return etymology, definitions

parts = ('preposition', 'particle', 'noun', 'verb',
    'adjective', 'adverb', 'initialism', 'interjection', 'prefix',
    'proper noun', 'determiner', 'pronoun', 'prepositional phrase',
    'conjunction', 'abbreviation', 'numeral', 'phrase', 'symbol',
    'participle', 'suffix')
# Make the below match the above, otherwise it's pointless :x
flagparts = dict(zip(('p','P','n','v',
    'a','A','i','j','r'),parts))

def format(word, definitions, number=2, force_part=None):
    result = '%s' % word.encode('utf-8')
    # if there is a definition for force_part use only that,
    # otherwise loop through parts
    for part in (parts if not force_part else (force_part,)):
        #print "Testing part: " + part + "(type: " + str(type(part)) + ", number " + str(number) + ")" #FIXME
        if definitions.has_key(part):
            defs = definitions[part][:number]
            result += u' \u2014 '.encode('utf-8') + ('%s: ' % part)
            n = ['%s. %s' % (i + 1, e.strip(' .')) for i, e in enumerate(defs)]
            result += ', '.join(n)
    return result.strip(' .,')

def getclass(input):
    """
    in:     "-s" or "--smeg"
    out:    "smeg" if in parts or if "s" in flagparts
    """
    if len(input) < 2:
        return None
    if len(input) == 2:
        if input[0] == '-' and input[1] in flagparts.keys():
            # valid "-s"
            return flagparts[input[1]]
        return None
    if input[:2] == '--' and input[2:] in parts:
        # valid "--smeg"
        # python 2 is dumb, convert to ascii
        return str(input[2:])
    return None

def wclass_word(input):
    """
    in:     "-s go on" or "--smeg go on"
    out:    ('smeg', 'go on')
    """
    # split on whitespace
    try:
        words = input.split()
    except: # input may be None
        return None, input
    if len(words) == 1:
        # single word
        return None, input
    # two args or more.
    part = getclass(words[0])
    word = ' '.join(words[1:])
    # valid part
    if part is not None:
        return part, word
    # invalid part
    return None, input

def define(jenni, input):
    #word = input.group(2)
    wclass, word = wclass_word(input.group(2))
    if not word:
        jenni.reply("You want the definition for what?")
        return
#    word = (word).lower()
    etymology, definitions = wiktionary(word)
    if not definitions:
        jenni.say("Couldn't get any definitions for %s at Wiktionary." % word)
        return

    result = format(word, definitions, force_part=wclass)
    if len(result) < 150:
        result = format(word, definitions, 3, force_part=wclass)
    if len(result) < 150:
        result = format(word, definitions, 4, force_part=wclass)
    if len(result) < 150:
        result = format(word, definitions, 5, force_part=wclass)
    if len(result) < 150:
        result = format(word, definitions, 6, force_part=wclass)

    formatted_uri = uri_ % web.urllib.quote(word.encode('utf-8'))
    uri_len = len(formatted_uri)
    max_len = 405 - uri_len

    if len(result) > max_len:
        result = result[:max_len] + ' ... ' + formatted_uri
    else:
        result = result + ' || ' + formatted_uri

    jenni.say(result)

define.commands = ['d', 'define', 'dict', 'w', 'word']
define.priority = 'high'
define.rate = 5
define.example = '.w bailiwick'

if __name__ == '__main__':
    print __doc__.strip()
