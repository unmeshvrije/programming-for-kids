from subprocess import Popen, PIPE
from io import StringIO
import os
import random
import sys
from itertools import cycle
from PIL import Image, ImageDraw, ImageFont
import time

HEIGHT = 1039
WIDTH = 744
COLS = 39
ROWS = 28
fnt = ImageFont.truetype('font.ttf', 33)

fgcolor = (20, 20, 20, 255)
border_color = (0, 0, 0, 100)
bgcolor = (0, 0, 0, 0)


def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def ignore_until_comment(line):
    ignore = True
    out = ''
    for s in line:
        if s == '#':
            ignore = False
        if not ignore:
            out += s
        else:
            out += ' '
    return out

def ignore_the_comment(line):
    in_comment = False
    out = ''
    for s in line:
        if s == '#':
            in_comment = True
        if in_comment:
            out += ' '
        else:
            out += s
    return out


def border(d, data, id):
    lines = []
    bottom = "'--------------------------------------'"
    top = '.-------------->  ' + str(id).zfill(3) + '  <---------------.'
    if id == -1:
        top = '.--------------------------------------.'
    around = []
    around.append(top)
    lines.append('')

    text = data.split('\n')
    if text[len(text)-1] == "":
        text.pop()
    if len(text) > ROWS:
        raise Exception(str(id) + "'s text has too many rows" + data)

    for i in range(ROWS):
        code = ''
        if i <= len(text) - 1:
            code = text[i]

        lines.append('  '+ignore_the_comment(code).ljust(COLS - 3, ' ')+' ')
        comment = ''
        if '#' in code:
            comment = ignore_until_comment(code)

        around.append('| ' + comment.ljust(COLS - 3, ' ') + ' |')

    lines.append('')
    around.append(bottom)

#    help = (20, 20, 20, 20)
#    size = 2
#    d.rectangle([0, 0, size, size], fill=help)
#    d.rectangle([WIDTH-size, HEIGHT-size, WIDTH, HEIGHT], fill=help)
#    d.rectangle([0, HEIGHT-size, size, HEIGHT], fill=help)
#    d.rectangle([WIDTH-size, 0, WIDTH, size], fill=help)


    d.multiline_text((42, 38), "\n".join(lines), font=fnt, fill=fgcolor)
    d.multiline_text((42, 38), "\n".join(around), font=fnt, fill=border_color)

def back(deck, id, numbers, html):
    img = Image.new('CMYK', (WIDTH, HEIGHT), color=bgcolor)
    d = ImageDraw.Draw(img)
    lines = []
    for n in numbers:
        lines.append(str(n).rjust(random.randint(0, COLS - 3), ' '))

    border(d, "\n".join(lines), -1)

    img.save(os.path.join('images', deck, 'back_card_' +
             str(id).zfill(3)+'.tiff'), compression="tiff_lzw")
    jpg = os.path.join('images', deck, 'back_card_' +
             str(id).zfill(3)+'.jpg')
    img.save(jpg)
    html.write('<img width="25%" src="' + jpg + '">')


def front(deck, id, code,html):
    img = Image.new('CMYK', (WIDTH, HEIGHT), color=bgcolor)
    d = ImageDraw.Draw(img)
    border(d, code, id)
    img.save(os.path.join('images', deck, 'front_card_' +
             str(id).zfill(3)+'.tiff'), compression="tiff_lzw")
    jpg = os.path.join('images', deck, 'front_card_' +
             str(id).zfill(3)+'.jpg')
    img.save(jpg)
    html.write('<img width="25%" src="' + jpg + '">')
    if int(id+1) % 4 == 0:
      html.write('<br>')

def cheat(deck, answers, numbers, html):
    i = 0
    for (n, a) in enumerate(list(chunks(answers, ROWS))):
        img = Image.new('CMYK', (WIDTH, HEIGHT), color=bgcolor)
        d = ImageDraw.Draw(img)
        border(d, "\n".join(a), -1)
        img.save(os.path.join(
            'images', deck, 'front_card_answers_'+str(n).zfill(3)+'.tiff'), compression="tiff_lzw")
        jpg = os.path.join(
            'images', deck, 'front_card_answers_'+str(n).zfill(3)+'.jpg')
        img.save(jpg)
        i += 1
        html.write('<img width="25%" src="' + jpg + '">')
    return i


def run(file):
    process = Popen(["/usr/local/bin/python3", file], stdout=PIPE)
    (output, err) = process.communicate()
    exit_code = process.wait()
    if exit_code != 0:
        raise Exception(file + " exitted with " + str(exit_code))
    return output

random.seed(time.time())
for deck in ['easy', 'medium', 'hardcore']:
    html = open(deck + '.html','w')
    try:
        images_path = os.path.join('images', deck)
        os.mkdir(images_path)
    except:
        pass
    files = [f for f in os.listdir(os.path.join('decks', deck)) if f.endswith(".py")]
    files.sort()
    print('printing', deck, 'deck, with', len(files), 'cards')
    seen = {}
    qa = []
    possible = set()
    for (i, file) in enumerate(files):
        fp = os.path.join("decks", deck, file)
        f = open(fp, "r")
        text = f.read()
        f.close()
        if text in seen:
            raise Exception("ALREADY SEEN: " + text)
        seen[text] = True
        _out = run(fp).decode().strip().split("\n")
        if len(_out) == 0:
            raise "NO OUTPUT: " + file
        for line in _out:
            possible.add(line)
            qa.append(str(i).zfill(3) + ": " + line)

        front(deck, i, text, html)

    shuffled = list(possible)
    print('possible results', len(possible), 'rows', ROWS)
    random.shuffle(shuffled)

    if len(shuffled) > ROWS:
        raise Exception(str(len(shuffled)) + ">" + str(ROWS))
    back(deck, 0, shuffled, html)

    cheatsheet = cheat(deck, qa, shuffled, html)

    a1 = 55
    print(deck, 'total number of cards:', cheatsheet + len(files),
          'cheatsheet:', cheatsheet, 'missing:', a1 - (cheatsheet + len(files)))
    print('*' * 40)
    html.close()
