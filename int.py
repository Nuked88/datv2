# -*- coding: utf-8 -*-
#!/usr/bin/python
# encoding=utf8
import sys
import io
import re

import os
import pymongo
import math
import time
from pprint import pprint
from collections import defaultdict
from math_mean import harmonic_mean, percentage
from itertools import takewhile, repeat, izip_longest
from multiprocessing import Pool

reload(sys)
sys.setdefaultencoding('utf-8')

from pymongo import MongoClient


def getNextSequence(collection, name):
    return collection.find_and_modify(query={'_id': name}, update={'$inc': {'seq': 1}}, new=True).get('seq')

# check if word already exist


def findW(word):
    conn()

    rows = conn.collectionw.find({"word": word})
    ind = 0
    for row in rows:
        ind += 1
        id = row["_id"]

    if ind == 0:
        a = ind
    else:
        a = id
#    dd  pprint(a)
    return a


def findL(storyS):
    conn()
    rows = conn.collectionl.find({"story": storyS})
    ind = 0
    for row in rows:
        ind += 1
        id = row["_id"]

    if ind == 0:
        a = ind
    else:
        a = id
#    dd  pprint(a)
    return a

# check if word already exist


def findWById(_id):
    conn()
    wor = ""
    rows = conn.collectionw.find({"_id": _id})

    for row in rows:
        wor = row["word"]
    return wor

# check if sin already exist


def findS(story):
    conn()
    rows = conn.collectiont.find({"story": story})
    ind = 0
    for row in rows:
        ind += 1
        id = row["_id"]

    if ind == 0:
        a = ind
    else:
        a = id
#      pprint(a)
    return a


def findH2(story_list, hm, liv):
    nstoryS = ""
    # calcolo sensibilità di variazione possibile tra due vettori
    # simili (parametro necessario per ricerca tramine media armonica)
    sens = sens_calc(story_list, hm)
    conn()
    # cerco nel db sinapspi con sensibilità compresa tra i due valori
    rows = conn.collectiont.find(
        {"hm": {"$gt": sens[0], "$lt": sens[1]}, "liv": liv})

    return rows


def checkVoid(stringa):
    control = 0
    stringa.replace("XX", "")
    stringa.replace("=", "")
    # nullo
    if stringa.strip() == "":
        control = 1
    else:
        control = 0
    return control


def findH(story_list, story, sax, liv):
    nstoryS = ""
    b = []
    fatt1 = 4
    fatt2 = 4
    # calcolo sensibilità di variazione possibile tra due vettori
    # simili (parametro necessario per ricerca tramine media armonica)
    conn()
    # cerco nel db sinapspi con sensibilità compresa tra i due valori
    rows = conn.collectiont.find(
        {"sax": {"$eq": sax}, "liv": liv, "story": {"$ne": story}})
    story_list1 = story.split("=")  # array story corrente
    wat1 = findD(story_list1)
    nstory1 = csax(story_list1)

    for r in rows:
        story_list2 = r['story'].split("=")  # array story restituito

        # verifica validità risultati comparando csax array
        nstory2 = csax(story_list2)
        if nstory1 == nstory2:
            wat2 = findD(story_list2)
            comp = compareA(wat1, wat2)
            for c in comp:
                b = wat1[c]
                # creazione regola in base al parametro variabile
                pprint("ilparametro che varia e' " +
                       str(comp[0]) + " presente nelle posizioni " + str(b))
            # il che significa che la regola deve dichiarare che per ogni sinapsi uguale a quella della regola e che ha nelle posizioni 2 e 4 un parametro uguale
            # dat deve sostituire alla posizione 4 il parametro 2 anche se non è presente una sinapsi per quello
            # sostituiamo il parametro alle coordinate ultime dell'array con XX
                nstory = []
                for w in story_list1:
                    if w == str(comp[0]):
                        a = "XX"
                        nstory.append(a)
                    else:
                        nstory.append(w)
                # back to string
                nstoryS = ''.join("=".join(str(x) for x in nstory))

            # se non esiste già la logica
            fatt1 = findL(nstoryS)
            fatt2 = checkVoid(nstoryS)
            if fatt1 == 0 and fatt2 == 0:
                pprint(nstoryS)
                idsinL = conn.collectionl.insert(
                    {"liv": liv, "story": nstoryS, "wtd": b, "sax": sax, "weight": 0})
            else:
                conn.collectionl.update_one(
                    {"_id": fatt1},
                    {
                        "$inc": {
                            "weight": 1
                        }
                    }
                )
                pprint(str(nstoryS) + " NON INSERITO GIA PRESENTE:" +
                       str(fatt1) + " INUTILE:" + str(fatt2))

            # pprint("wat1"+str(wat1))
            # pprint("wat2"+str(wat2))
            # for index,w in wat1.items():
            #    pprint(w)
     # pprint(hm)
        else:
            pass


# trova duplicati nella lista con posizione
def findD(mylist):
    D = defaultdict(list)
    for i, item in enumerate(mylist):
        D[item].append(i)
    D = {k: v for k, v in D.items() if len(v) > 1}
    return D

# confronta due liste e trova le differnze


def compareA(mylist1, mylist2):
    s = set(mylist2)
    mylist3 = [x for x in mylist1 if x not in s]
    return mylist3


def upcolNext(idsin, idn):
    conn()
    conn.collectiont.update_one(
        {"_id": idsin},
        {
            "$set": {
                "next": idn
            }
        }
    )


def csax(data):
    nstory = []
    # trovo valori ripetuti se esistono
    wat = findD(data)
    s = 0
    # elimino i valori ripetuti
    for w in data:
        if w in wat:
            pass
        else:
            nstory.append(w)
    # restituisco l'array

    return nstory


def nsax(data, limit):
    sax = 0
    maxx = 0
    if limit == 0:
        limit = len(data)
    _sax = csax(data)
    for n in _sax:
        if maxx < limit:
            sax += int(n)
            maxx += 1
    return sax


def sens_calc(data, hm1):
            # cambio un valore (se si ripete devo variare anche l'altro)
            # lista valori -> prendo un valore random-> ricerco tutti quei valori nella lista e li sostituisco
            # ECCEZIONE: se tutti i valori sono uguali salto tutto
            # per comnodità varieremo solo il primo
    v = data[0]
    conn()
    maxW = conn.collectionw.count()
    data = [str(l) for l in data]
    datam = [w.replace(str(v), str(maxW)) for w in data]
    datam = [float(l) for l in datam]
    hm2 = harmonic_mean(datam)
    hmm = (hm2 / hm1)
    pw = 0.333333
    grow = (math.pow(hmm, pw) - 1) * 100
    vari = percentage(grow, hm1)
    vmin = hm1 - vari
    vmax = hm1 + vari

    return [vmin, vmax]


def trainAI(stri):
    # split speak
    words = stri.split()
    conn()
    # create insert word and create link
    i = 0

    maxx = len(words)
    story = ""
    idsin = ""

    for word in words:
        liv = i
        sax = 0
        if liv == 0:
            if findW(word) == 0:
                    # trovo id associati alle parole
                _id = conn.collectionw.insert(
                    {"_id": getNextSequence(conn.db.counters, "nodeid"), "word": word})
                story = _id
            else:
                story = findW(word)

        elif liv != 0 and i < maxx:
            if findW(word) == 0:
                _id = conn.collectionw.insert(
                    {"_id": getNextSequence(conn.db.counters, "nodeid"), "word": word})
            else:
                _id = findW(word)

            story = str(story) + "=" + str(_id)
            # da stringa a lista
            story_list = story.split("=")
            story_list = [float(y) for y in story_list]
            # media armonica
            hm = harmonic_mean(story_list)
            # calcolo la somma assoluta
            sax = nsax(story_list, 0)

            # aggiorno ultimo sin con prossimo id
            upcolNext(idsin, _id)
            # detect repetition

            # inserisco nuovo sin se non esite
            if findS(story) == 0:
                idsin = conn.collectiont.insert(
                    {"liv": liv, "story": story, "next": "", "hm": hm, "sax": sax, "weight": 0})
            else:
                idsin = findS(story)
                conn.collectiont.update_one(
                    {"_id": idsin},
                    {
                        "$inc": {
                            "weight": 1
                        }
                    }
                )

            findH(story_list, story, sax, liv)
            #             print("esiste")
        i += 1
    return "ok"

# repetition rule


def rrule(data):

    conn()
    data = data.split("=")
    asw = []
    story = ''.join("=".join(str(x) for x in data))
    nstory2 = []
    # cerco sax corrente
    sax = nsax(data, 0)
    rows = conn.collectionl.find(
        {"story":  {"$regex": story + ".*"}})

    wat1 = findD(data)
    nstory1 = csax(data)

    for r in rows:

        rule = r['story'].split("=")  # array story restituito
        wtd = r['wtd']
        take = wtd[0]
        put = wtd

        # ricrea una storia con la regola
        for p in put:
            rule[int(p)] = data[int(take)]

        # costruisco la frase togliendo cio che è già stato detto
        liv = len(data)
        rule = rule[liv:]
        for r in rule:
            asw.append(str(findWById(int(r))).strip())

    return asw


def bringLevelDown(data, liv):
    return data[:liv]


def interact(stri):
    conn()
    # split speak
    next = 0
    str1 = []
    aws = []
    stop = 2
    i = 0
    i2 = 0
    hm = 0
    words = stri.split()

    # liv = len(words)
    for word in words:
        liv = i
        if findW(word) == 0:
                    # trovo id associati alle parole se non c'è la inserisco
            conn.collectionw.insert(
                {"_id": getNextSequence(conn.db.counters, "nodeid"), "word": word})
        str1.append(str(findW(word)).strip())
        i = + 1

    str2 = list(str1)

    story = ''.join("=".join(str(x) for x in str1))
    rex = "^(" + story + ").*"
    rows = conn.collectiont.find({"story": {'$regex': rex}})
    # pprint(str1)
    vartemp = story
    # se non ci sono risultati diminuisco di uno l'array
    pprint(rows.count())
    # row count
    rc = rows.count()
    # len str2
    ls2 = len(str2)

    if rc == 0:
        stop = 0
    # non va x me
    while stop == 0:
        pprint("inutile")
        str2.pop(-1)
        ls2 = ls2 - 1
        story = ''.join("=".join(str(x) for x in str2))
        if rc != 0 or ls2 == 0:
            # se non c'è nemmeno un collegamento vado di regola... non so se
            # fare il contrario

            stop = 1

            # pprint("stoppo con array "+str(str1))

    while(next != ""):

        pprint("Loop, stop:" + str(stop))
        if stop == 2:
            # test: inizio con il primo e basta.
            pprint("inizio ciclo 2 con i2:" + str(i2))
            if i2 == 0:
                row = rows[0]
                next = row['next']
                if hm != 0:
                    story = row['story']
                    s2 = story.split("=")

                    for s in s2:
                        s = int(s)
                        aws.append(findWById(s))

                aws.append(findWById(next))

            else:
                for row in rows:
                    next = row['next']
                    aws.append(findWById(next))

            # aggiorno la story per cercare il prossimo next
            story = story + '=' + str(next)
            rows = conn.collectiont.find({"story": story})
            pprint("sss" + story)
            pprint("sss" + str(aws))

            if rows.count() == 0:
                next = ""

            if row['next'] == "":
                next = ""
                # next = ""
             #   pprint("nores")

        elif stop == 1:
            pprint("ciclo armonico")
            # cerco quindi in Logic una regola tipo 1=2=0 con campo wtd (what to do) che deve essere tipo [1,4] e vuol dire che quello che è nella pos 1 della
            # mia story lo metto anche nella posizione 4 della story finale
            # scritta nel campo fstory della regola
            try:
                aws = rrule(vartemp)
                pprint(len(aws))
                # no rule
                if len(aws) == 0:
                    # nessun risultato
                    # provo con la media armonica
                    story_list = [float(y) for y in str1]
                    # media armonica
                    hm = harmonic_mean(story_list)
                    rows = findH2(story_list, hm, liv)
                    # pprint(liv)
                    # se cmq è ancora a 0
                    if rows.count() == 0:
                        next = ""
                    else:
                        i2 = -1
                        stop = 2

            except:
                pass

            #next = ""
            # fermo il ciclo

        i2 = i2 + 1
        answer = ' '.join(aws)
    return answer


def rawbigcount(filename):
    f = open(filename, 'rb')
    bufgen = takewhile(lambda x: x, (f.read(1024 * 1024)
                                     for _ in repeat(None)))
    return sum(buf.count(b'\n') for buf in bufgen if buf)


def grouper(n, iterable, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    # grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx
    args = [iter(iterable)] * n
    return zip_longest(fillvalue=fillvalue, *args)


def splitBig(name, maxFile):
    rangeC = 1
    rangeC = rawbigcount(name)
    # sempre numero intero
    while rangeC % maxFile == 0:
        rangeC = rangeC + 1

    n = (rangeC / maxFile)

    with open(name) as f:
        for i, g in enumerate(grouper(n, f, fillvalue=''), 1):
            with open('./train/small_file_{0}'.format(i), 'w') as fout:
                fout.writelines(g)


def train(index):
    pprint("ok")
    # cerco se ci sono dei progressi
    progFile = "./train/progress{0}.txt".format(index)
    trainFile = "./train/small_file_{0}".format(index)
    if os.path.exists(progFile):
        f = open(progFile, "r")
        ind = f.read().strip()
        if ind != "":

            pprint(ind)
            i = int(ind)
        else:
            pprint("No progress saved or progress lost!")
            i = 0
        f.close()

    else:
        i = 0

    rangeC = rawbigcount(trainFile)
    non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
    files = io.open(trainFile, "r", encoding="utf8")
    str1 = ""
    str2 = ""

    filex = open(progFile, "w")

    # progressbar usage
    for line in files:
        line = line.replace("\n", "")
        if i % 2 == 0:
            str1 = line.translate(non_bmp_map)
        else:
            str2 = line.translate(non_bmp_map)

        trainAI(str1 + " " + str2)
        filex.seek(0)
        filex.truncate()
        filex.write(str(i))
        sys.stdout.write("Progress:" + str(i) + "/" + str(rangeC))
        i += 1


def getInput():
    while(0 == 0):
        text = raw_input("Please enter something: ")
        s = interact(text)
        print(s)

maxProcess = 2
#splitBig('./train/train.txt', 2)
# multiprocessing trainig


def conn():

    #conn.db = MongoClient('mongodb://nuked:112358@192.168.1.3:27017/?authMechanism=DEFAULT&authSource=morphit')
    conn.db = MongoClient('192.168.1.3').morphit
    conn.db.authenticate('nuked', '112358', mechanism='SCRAM-SHA-1')
    conn.collectionw = conn.db['words']
    conn.collectiont = conn.db['sinMemo']
    conn.collectionl = conn.db['sinLogic']


def f(i):
    conn()
    train(i)


if __name__ == '__main__':
    pprint("Start")
    # getInput()
    f(1)
    #p = Pool(maxProcess)
    #print(p.map(f, [1, 2]))

    #
    # text = "ciao sono A151edo"

    # train()
    # s = trainAI(text)

    # print s
