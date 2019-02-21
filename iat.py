# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import csv
import random
import functools
import helpers2 as helpers
import psychopy.visual
from psychopy import visual, event, core, gui
from copy import deepcopy as cp
import os
import glob
import numpy as np

maindir = os.getcwd()
wyniki = './wyniki'

result_name = "experiment_paraolympics_"
os.chdir(wyniki)
list_of_files = glob.glob(result_name+'*')
list_of_numbers = []
for i in list_of_files:
    nb = int(i[len(result_name):-4])
    list_of_numbers.append(nb)
if len(list_of_numbers)==0:
    new_file_number = 1
else:
    new_file_number = np.max(list_of_numbers)+1
info = {'ID':[new_file_number]}
os.chdir(maindir)

# get user data before setup, since Dlg does not work in fullscreen
# can be used to ask for any input that is needed
#title = 'SIP IAT'
#questions = {'ID': '', 'Condition': ['A', 'B']}
#questions = {'ID': ''}
#info = helpers.getInput(title, questions) or core.quit()


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
A, B = ['dobre', 'zle'], ['paraolimpiada', 'olimpiada']
TEST_category = ['lewo', 'prawo']
allRes = A+B
allMappings = helpers.getResponseMappings(allRes, keybindings=keybindings)

leftup, rightup = (-0.8, +0.8), (+0.8, +0.8)
leftdown, rightdown = (-0.8, +0.7), (+0.8, +0.7)
directions = [(-0.8, +0.8), (+0.8, +0.8), (-0.8, +0.7), (+0.8, +0.7)]

experimentData = []
timer = core.Clock()
# you can easily change the stimuli by changing the csv
stimuli = helpers.getStimuli('stimuli_filler.csv')

ISI = 0.150
TIMEOUT = 1.5
feedbackTime = 1

def block(anchors, responseMap, selection, trialName, trials=20):
    data = []
    helpers.autodraw(anchors)

    filteredStim = helpers.filterStimuli(stimuli, 'response', *selection)
    extendedStim = helpers.compensate(filteredStim, trials)

    randomStim = sorted(extendedStim, key=lambda x: random.random())[:trials]
    preparedStim = helpers.deneigh(randomStim)

    for stimulus in preparedStim:
        helpers.autodraw(anchors, draw=True)
        onTime = True
        content = stimulus['content']
        if content[-4:] in ['.jpg', '.png']:
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
            core.quit()
        else:
            RT = timer.getTime()
            onTime = False
            draw(negFeedback, feedbackTime)
            draw(curStim)
            event.waitKeys(keyList=[rightAnswer])
        data.append([ISI, content, int(onTime), RT, trialName])
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
            cat_title += "_"+category2[1]+"_"+category2[0]

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

ntrials = 3

allBlocks = {
    1: wrapping(TEST_category, keybindings, directions, False, False, False, ntrials),
    2: wrapping(A, keybindings, directions, False, False, False, ntrials),
    3: wrapping(A, keybindings, directions, True, False, False, ntrials),
    4: wrapping(B, keybindings, directions, False, False, False, ntrials),
    5: wrapping(B, keybindings, directions, True, False, False, ntrials),
    6: wrapping(A, keybindings, directions, False, B, False, ntrials),
    7: wrapping(A, keybindings, directions, False, B, False, ntrials),
    }

mainInstruction = u'''
    Połóż palce wskazujące na klawisze 'e' oraz 'i', abyś był gotowy(a), do jak najszybszego udzielania odpowiedzi.
    Słowa i obrazki grupuj za pomocą klawisza 'e' lub 'i' zgodnie z nazwami kategorii znajdującymi się u góry ekranu
    Każde słowo lub obrazek można zaklasyfikować do jednej kategorii. Większość kategoryzacji nie powinna sprawiać problemu.
    Klasyfikuj bodźce zgodnie z ich kategorią. Obrazki oraz zielone słowa należą do kategorii zaznaczonych na zielono. Analogicznie, słowa w kolorze białym powinny być przyporządkowane do białych kategorii.
    Jeżeli zadanie wykonujesz zbyt wolno, wówczas program nie generuje wyniku. Proszę, postaraj się wykonywać test najszybciej, jak potrafisz.
    Jeśli test wykonujesz szybko, mogą zdarzyć się przypadkowe błędy. Nie stanowi to jednak problemu.
    Aby uzyskać lepszy rezultat, unikając zakłóceń podczas wykonywania testu, ustaw, proszę, w monitorze maksymalną jasność.
'''

endInstruction = u'''Dziękujemy za badanie'''

instructions = {
        1: u'''Teraz przyzwyczaisz się do zadania. Na pojawiające się słow 'lewo' naciśnij klawisz 'e', na pojawiające się słowo 'prawo' naciśnij jak najszybciej klawisz 'i'. ''',
        2: u'''testowa instrukcja''',
        3: u'''testowa instrukcja''',
        4: u'''testowa instrukcja''',
        5: u'''testowa instrukcja''',
        6: u'''testowa instrukcja''',
        7: u'''testowa instrukcja'''}

def main():
    # Instruction Setup
    header = ['ISI', 'Content', 'corrAns', 'RT', 'trialName']

    show(text=mainInstruction, height=0.07, wrapWidth=1.5, font='Arial')

    # order in which the data are analyzed

    # this can be made to randomly choose between two (or more) order types
    # trialType = random.randint(0, 1) #1
    # order = [1, 2, 3, 5, 6,7] if trialType else [5, 2, 6, 1, 3]

    order = [1,2,4,6]
    #order = [1,2,3,4,5,6,7]

    # order the blocks and instruction according to the trialType
    blockOrder = [allBlocks[num] for num in order]
    instructionOrder = [instructions[num] for num in order] # maybe instructions can be text, not images? it probably is implemented
    data = helpers.runExperiment(show, instructionOrder, blockOrder)

    ## Save Data to CSV
    # experimentData.extend([info.values(), header])
    # experimentData.extend([new_file_number, header])
    experimentData.extend([header])
    experimentData.extend(data)

    os.chdir(wyniki)
    file = result_name+ str(new_file_number)+'.csv' # {0}.csv'.format(info['ID'])
    helpers.saveData(file, experimentData)
    show(text=endInstruction, font='Arial')
    win.close()
    core.quit()
    os.chdir(maindir)
main()
