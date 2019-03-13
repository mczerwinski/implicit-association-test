# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import csv
import random
import functools
import helpers as helpers
import psychopy.visual
from psychopy import visual, event, core, gui
from copy import deepcopy as cp
import os
import glob
import numpy as np

maindir = os.getcwd()
wyniki = './wyniki'

result_name = "experiment_olympics_"

# this part is to create a new name for the results
os.chdir(wyniki)
list_of_files = glob.glob(result_name+'*')
list_of_numbers = []
for i in list_of_files:
    nb = int(i[len(result_name):-4])
    list_of_numbers.append(nb)
#if len(list_of_numbers)==0:
#    new_file_number = 1
#else:
#    new_file_number = np.max(list_of_numbers)+1
#info = {'ID':[new_file_number]}
os.chdir(maindir)

# get user data before setup, since Dlg does not work in fullscreen
# can be used to ask for any input that is needed
title = 'IAT window'
#questions = {'ID': '', 'Condition': ['A', 'B']}
questions = {'ID': ''}
info = helpers.getInput(title, questions) or core.quit()
#info['number'] = new_file_number
if int(info['ID']) in list_of_numbers:
    print(u"Podany numer ", info['ID'], u'już występuje')
    raise SystemExit

# create all the basic objects (window, fixation-cross, feedback)
win = visual.Window(units='norm', color='black', fullscr=True)
fixCross = visual.TextStim(win, text='+', height=0.1)
negFeedback = visual.TextStim(win, text='X', color='red', height=0.1)
win.setMouseVisible(False)

# partially apply the helper functions to suite our needs
draw = functools.partial(helpers.draw, win)
show = functools.partial(helpers.showInstruction, win)
wrapdim = functools.partial(helpers.wrapdim, win, height=0.08)

# Response Mappings
# you can change the keybindings and allRes to fit your IAT constraints
keybindings = ['e', 'i']
A = ['pozytywne', 'negatywne']
B = ['paraolimpiada', 'olimpiada']
TEST_category = ['lewo', 'prawo']
allRes = A+B
allMappings = helpers.getResponseMappings(allRes, keybindings=keybindings)

leftup, rightup = (-0.8, +0.8), (+0.8, +0.8)
leftdown, rightdown = (-0.8, +0.7), (+0.8, +0.7)
directions = [(-0.8, +0.8), (+0.8, +0.8), (-0.8, +0.7), (+0.8, +0.7)]

experimentData = []
timer = core.Clock()
# you can easily change the stimuli by changing the csv
stimuli = helpers.getStimuli('stimuli.csv')

ISI = 0.150
TIMEOUT = 1.5
feedbackTime = 1

def block(anchors, responseMap, selection, trialName, trials=20):
    data = []
    helpers.autodraw(anchors)
    filteredStim = helpers.filterStimuli(stimuli, 'response', *selection) #this is ok
    extendedStim = helpers.compensate(filteredStim, trials) # this is ok

    randomStim = sorted(extendedStim, key=lambda x: random.random())[:trials]
    #preparedStim = helpers.deneigh(randomStim)
    preparedStim = randomStim
    for stimulus in preparedStim:
        helpers.autodraw(anchors, draw=True)
        onTime = True
        content = stimulus['content']
        if helpers.isImage(content): #[-4:] in ['.jpg', '.png']:
            if content[0] == '/':
                proper_content = '.'+content
            else:
                proper_content = content

            curStim = visual.ImageStim(win, proper_content, size=(0.7,0.7))#, height=0.1)
        else:
            curStim = visual.TextStim(win, text=content, height=0.1, font='Arial')

        rightAnswer = responseMap[stimulus['response']]
        rightKeys = list(responseMap.values()) + ['escape'] #changed to list
        anchors[0].draw()
        anchors[1].draw()
        if len(anchors)>2:
            anchors[2].draw()
            anchors[3].draw()

        draw(curStim)
        timer.reset()
        userAnswer = event.waitKeys(keyList=rightKeys) or []
        choseWisely = helpers.equals(userAnswer, rightAnswer)
        if choseWisely:
            RT = timer.getTime()
        elif 'escape' in userAnswer:
            win.close()
            core.quit()
        else:
            RT = timer.getTime()
            onTime = False
            draw(negFeedback, feedbackTime)
            anchors[0].draw()
            anchors[1].draw()
            if len(anchors)>2:
                anchors[2].draw()
                anchors[3].draw()
            draw(curStim)

            event.waitKeys(keyList=[rightAnswer])

        data.append([stimulus['item'], content, int(onTime), RT, trialName])
        draw(fixCross, ISI)
    return data

def wrap(*args, **kwargs):
    return functools.partial(block, *args, **kwargs)

def wrapping(category, buttons, directions, flipA=False, category2=False, flipB=False, ntrials=20):
    cat_title = ''
    if flipA:
        a, b = directions[1], directions[0]
        abutton, bbutton = buttons[1], buttons[0]
        cat_title = category[1]+"_"+category[0]
    else:
        a, b = directions[0], directions[1]
        abutton, bbutton = buttons[0], buttons[1]
        cat_title = category[0]+"_"+category[1]

    if category2 is not False:
        cat_title == "_"
        if flipB:
            c, d = directions[3], directions[2]
            cbutton, dbutton = buttons[1], buttons[0]
            cat_title += "_"+category2[1]+"_"+category2[0]
        else:
            c, d = directions[2], directions[3]
            cbutton, dbutton = buttons[0], buttons[1]
            cat_title += "_"+category2[0]+"_"+category2[1]
            #INCORRECT BELOW!!
            #cat_title += "_"+category2[1]+"_"+category2[0]
    d_annot ={}
    d_annot[category[0]] = a
    d_annot[category[1]] = b
    if category2 is not False:
        d_annot[category2[0]] = c
        d_annot[category2[1]] = d
    d_keys = {}
    d_keys[category[0]] = abutton
    d_keys[category[1]] = bbutton
    if category2 is not False:
        d_keys[category2[0]] = cbutton
        d_keys[category2[1]] = dbutton

    category_list = cp(category)
    if category2 is not False:
        category_list += category2

    annotations = wrapdim(d_annot)
    blockthing = wrap(annotations, d_keys, category_list, cat_title, trials=ntrials)
    return blockthing

ntrials = 12

allBlocks = {
    1: wrapping(TEST_category, keybindings, directions, False, False, False, ntrials),
    2: wrapping(A, keybindings, directions, False, False, False, ntrials),
    3: wrapping(A, keybindings, directions, True, False, False, ntrials),
    4: wrapping(B, keybindings, directions, False, False, False, ntrials),
    5: wrapping(B, keybindings, directions, True, False, False, ntrials),
    6: wrapping(A, keybindings, directions, False, B, False, ntrials),
    7: wrapping(A, keybindings, directions, False, B, True, ntrials),
    8: wrapping(A, keybindings, directions, True, B, False, ntrials),
    9: wrapping(A, keybindings, directions, True, B, True, ntrials)
    }

def instrukcja_prosta(kat1, kat2):
    text = u'''
{0}                                                                                           {1}

UWAGA – spójrz, teraz zmieniły się kategorie. Jeżeli dany bodziec należy do kategorii znajdującej się po lewej stronie , naciśnij klawisz  E. Jeżeli dany bodziec należy do kategorii należącej po prawej stronie naciśnij I. Każde słowo lub obrazek należy do jednej kategorii. Jeżeli popełnisz błąd przy porządkowaniu, na ekranie pojawi się czerwony  X – wtedy popraw błąd, naciskając  drugi klawisz
Jest to zadanie na czas. Postaraj się wykonać je JAK NAJSZYBCIEJ POTRAFISZ, jednocześnie popełniając jak najmniej błędów. Zbyt wolne wykonanie zadania i popełnienie zbyt wielu błędów prowadzi do wyników, których nie można zinterpretować. Zadanie zajmuje około 5 minut
ABY ROZPOCZĄĆ TEST WCIŚNIJ SPACJĘ'''.format(kat1, kat2)
    return text

def instrukcja_zlozona(a1, a2, b1, b2):
    tekst = u'''
{0}                                                                                           {1}
+                                                                                             {4}+
{2}                                                                                           {3}

Spójrz na górę ekranu, kategorie, które wyświetlały się poprzednio, teraz znajdują się razem. Pamiętaj, że każdy bodziec należy tylko do jednej grupy. Przyporządkuj wyświetlające się słowa lub zdjęcia do prawych lub lewych grup, przy pomocy klawiszy E (prawa strona) lub I (lewa strona).
Jeżeli popełnisz błąd przy porządkowaniu, na ekranie pojawi się czerwony  X – wtedy popraw błąd, naciskając  drugi klawisz
ABY KONTYNUOWAĆ WCIŚNIJ SPACJĘ'''.format(a1, a2, b1, b2, len(a1)*" ")
    return tekst

mainInstruction = u'''
    Połóż palce wskazujące na klawisze 'e' oraz 'i', abyś był gotowy(a), do jak najszybszego udzielania odpowiedzi.
    Słowa i obrazki grupuj za pomocą klawisza 'e' lub 'i' zgodnie z nazwami kategorii znajdującymi się u góry ekranu
    Każde słowo lub obrazek można zaklasyfikować do jednej kategorii. Większość kategoryzacji nie powinna sprawiać problemu.
    Klasyfikuj bodźce zgodnie z ich kategorią. Obrazki oraz zielone słowa należą do kategorii zaznaczonych na zielono. Analogicznie, słowa w kolorze białym powinny być przyporządkowane do białych kategorii.
    Jeżeli zadanie wykonujesz zbyt wolno, wówczas program nie generuje wyniku. Proszę, postaraj się wykonywać test najszybciej, jak potrafisz.
    Jeśli test wykonujesz szybko, mogą zdarzyć się przypadkowe błędy. Nie stanowi to jednak problemu.
    Aby uzyskać lepszy rezultat, unikając zakłóceń podczas wykonywania testu, ustaw, proszę, w monitorze maksymalną jasność.
'''

endInstruction = u'''Dziękujemy za badanie
'''

instrukcja_prawo_lewo = u'''
LEWO                                                                                           PRAWO

Połóż palce na klawiszach E oraz I. W tym zadaniu sprawdzany jest Twój czas reakcji. Naciśnij "E" - lewy klawisz, jeżeli pojawi się słowo LEWO. Naciśnij "i" - prawy klawisz jeżeli pojawi się słowo PRAWO. Jeżeli popełnisz błąd przy porządkowaniu, na ekranie pojawi się czerwony  X – wtedy popraw błąd, naciskając  drugi klawisz.
Jest to zadanie na czas. Postaraj się wykonać je JAK NAJSZYBCIEJ POTRAFISZ, jednocześnie popełniając jak najmniej błędów.
ABY ROZPOCZĄĆ TEST WCIŚNIJ SPACJĘ
'''

instructions = {
        1: instrukcja_prawo_lewo,
        2: instrukcja_prosta(A[0], A[1]),
        3: instrukcja_prosta(A[1], A[0]),
        4: instrukcja_prosta(B[0], B[1]),
        5: instrukcja_prosta(B[1], B[0]),
        6: instrukcja_zlozona(A[0], A[1], B[0], B[1]),
        7: instrukcja_zlozona(A[0], A[1], B[1], B[0]),
        8: instrukcja_zlozona(A[1], A[0], B[0], B[1]),
        9: instrukcja_zlozona(A[1], A[0], B[1], B[0])

    }
#mainInstruction = '/instrukcje/instrukcja_glowna.png'
#instructions = {
#        1: '/instrukcje/lewo_prawo.png',  # powinno byc lewo_prawo.png
#        2: '/instrukcje/pozytywne_negatywne.png',
#        3: '/instrukcje/negatywne_pozytywne.png',
#        4: '/instrukcje/paraolimpiada_olimpiada.png',
#        5: '/instrukcje/olimpiada_paraolimpiada.png',
#        6: '/instrukcje/paraolmpiada_pozytywne_olimpiada_negatywne.png',
#        7: '/instrukcje/olimpiada_pozytywne_paraolimpiada_negatywne.png',
#        8: '/instrukcje/paraolimpiada_negatywne_olimpiada_pozytywne.png'
#    }
def main():
    # Instruction Setup

    show(text=mainInstruction, height=0.06, wrapWidth=1.6, font='Arial')

    # order in which the data are analyzed

    # this can be made to randomly choose between two (or more) order types
    order1 = [1, 2, 4, 7, 3, 5, 6, 1]
    order0 = [1, 3, 4, 9, 2, 5, 8, 1]


    trial_random = random.random()
    trialType = random.randint(0, 1) #1
    if trial_random<0.5:
        trialType = 0
    else:
        trialType = 1

    #TrialType set HARD on group 0:
    #trialType=0

    if trialType==0:
        order = order0
    elif trialType==1:
        order = order1

    header = ['number of stimulation', 'Content', 'corrAns', 'RT', 'trialName', 'trialType:', str(trialType)]

    # order the blocks and instruction according to the trialType
    blockOrder = [allBlocks[num] for num in order]
    instructionOrder = [instructions[num] for num in order]
    data = helpers.runExperiment(show, instructionOrder, blockOrder)

    ## Save Data to CSV
    # experimentData.extend([info.values(), header])
    # experimentData.extend([new_file_number, header])
    experimentData.extend([header])
    experimentData.extend(data)

    os.chdir(wyniki)
    file = result_name+ str(info['ID'])+'.csv' # {0}.csv'.format(info['ID'])
    helpers.saveData(file, experimentData)
    show(text=endInstruction+u'wersja testu: '+str(trialType), font='Arial', wrapWidth=1.5)
    win.close()
    core.quit()
    os.chdir(maindir)

main()
os.chdir(maindir)
