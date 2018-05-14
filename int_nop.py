# -*- coding: utf-8 -*-
#!/usr/bin/python
# encoding=utf8
import sys
import getopt
import io
import re
import string
import random
import os
import pymongo
import math
import time
from pprint import pprint
from collections import defaultdict
from math_mean import harmonic_mean, percentage,F
from itertools import takewhile, repeat, izip_longest
from multiprocessing.dummy import Pool as ThreadPool 


reload(sys)
sys.setdefaultencoding('utf-8')

from pymongo import MongoClient
db = MongoClient().morphit
db.authenticate('nuked', 'test', mechanism='SCRAM-SHA-1')
collectionw = db['words']
collectiont = db['sinMemo']
collectionl = db['sinLogic']
collectionm = db['DNA']
inputfile = 0
outputfile = 0
maxEnd=0
deb = 0

def getNextSequence(collection, name):
    return collection.find_and_modify(query={'_id': name}, update={'$inc': {'seq': 1}}, new=True).get('seq')

# check if word already exist


def findW(word):

    if deb == 1:
        pprint("FindW")
    rows = collectionw.find({"word": word}).limit(1)
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

    if deb == 1:
        pprint("FindL")
    rows = collectionl.find({"story": storyS}).limit(1)
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


def findGen(name):
    if deb == 1:
        pprint("Find"+str(name))
    rows = collectionm.find({name:{ '$exists': 'dna' }}).limit(1)
    ind = 0
    for row in rows:
        ind += 1
        id = row[name]



    if ind == 0:
        a = ind
    else:
        a = id
#    dd  pprint(a)
    return a

# check if word already exist
def findWById(_id):
    s=0
    e=0
    if deb == 1:
        pprint("FindWById"+str(_id))
    wor = ""
    rows = collectionw.find({"_id": _id}).limit(1)

    for row in rows:

        wor = row["word"]
        s= row["start"]
        e=row["end"]
    return wor,s,e

def findWByIdFull(_id):

    wor = ""
    rows = collectionw.find({"_id": _id})

    for row in rows:
        wor = row
    return wor

# check if sin already exist


def findS(story):

    if deb == 1:
        pprint("FindS")
    rows = collectiont.find({"story": story}).limit(1)
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
    if deb == 1:
        pprint("FindH2"+str(story_list))
    nstoryS = ""
    # calcolo sensibilità di variazione possibile tra due vettori
    # simili (parametro necessario per ricerca tramine media armonica)
    sens = sens_calc(story_list, hm)

    # cerco nel db sinapspi con sensibilità compresa tra i due valori
    rows = collectiont.find(
        {"hm": {"$gt": sens[0], "$lt": sens[1]}, "liv": liv})

    return rows


def checkVoid(stringa):
    if deb == 1:
        pprint("checkVoid"+stringa)
    control = 0
    stringa.replace("XX", "")
    stringa.replace("=", "")
    # nullo
    pprint("stringafinale:" + stringa)
    if stringa.strip() == "":
        control = 1
    else:
        control = 0
    return control


def findH(story_list, story, sax, liv):
    if deb == 1:
        pprint("FindH"+str(story_list))

    nstoryS = ""
    b = []
    fatt1 = 4
    fatt2 = 4
    # calcolo sensibilità di variazione possibile tra due vettori
    # simili (parametro necessario per ricerca tramine media armonica)

    # cerco nel db sinapspi con sensibilità compresa tra i due valori
    rows = collectiont.find(
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
              #  pprint("ilparametro che varia e' " +
              #         str(comp[0]) + " presente nelle posizioni " + str(b))
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
                if liv == 1:
                    idsinL = collectionl.insert(
                        {"liv": liv, "story": nstoryS, "wtd": b, "sax": sax, "weight": 0, "start": 1})
                else:
                    idsinL = collectionl.insert(
                        {"liv": liv, "story": nstoryS, "wtd": b, "sax": sax, "weight": 0, "start": 0})

            else:

                collectionl.update_one(
                    {"_id": fatt1},
                    {
                        "$inc": {
                            "weight": 1
                        }
                    }
                )
                if liv == 1:
                    collectionl.update_one(
                        {"_id": fatt1},
                        {
                            "$inc": {
                                "start": 1
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

    collectiont.update_one(
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

    maxW  = collectionw.count()
    data  = [str(l) for l in data]
    datam = [w.replace(str(v), str(maxW)) for w in data]
    datam = [float(l) for l in datam]
    hm2  = harmonic_mean(datam)
    hmm  = (hm2 / hm1)
    pw   = 0.333333
    grow = (math.pow(hmm, pw) - 1) * 100
    vari = percentage(grow, hm1)
    vmin = hm1 - vari
    vmax = hm1 + vari

    return [vmin, vmax]


def trainAI(stri):
    # split speak
    words = stri.split()

    # create insert word and create link
    i = 0

    maxx = len(words)  # numero parole
    maxxr=maxx-1;
    story = ""
    idsin = ""

    for word in words:
        liv = i
        sax = 0
        if liv == 0:
            if findW(word) == 0:
                    # trovo id associati alle parole altrimenti la inserisco
                _id = collectionw.insert(
                    {"_id": getNextSequence(db.counters, "nodeid"), "word": word, "start": 1, "end": 0})
                story = _id
            else:
                story = findW(word)
                # se è la prima parola della frase incremento il valore di
                # start
                collectionw.update_one(
                    {"_id": story},
                    {
                        "$inc": {
                            "start": 1
                        }
                    }
                )
        elif liv != 0 and i < maxx:
            if findW(word) == 0:
                # se è l'ultima parola e non esiste
                if i == maxxr:
                    _id = collectionw.insert(
                        {"_id": getNextSequence(db.counters, "nodeid"), "word": word, "start": 0, "end": 1})
                else:
                    _id = collectionw.insert(
                        {"_id": getNextSequence(db.counters, "nodeid"), "word": word, "start": 0, "end": 0})

            else:
                # se è l'ultima parola ed esiste
                _id = findW(word)
                if i == maxxr:
                    collectionw.update_one(
                        {"_id": _id},
                        {
                            "$inc": {
                                "end": 1
                            }
                        }
                    )

            story = str(story) + "=" + str(_id)
            # da stringa a lista
            story_list = story.split("=")
            story_list = [float(y) for y in story_list]
            # media armonica
           # hm = harmonic_mean(story_list)
            # calcolo la somma assoluta
            sax = nsax(story_list, 0)

            # aggiorno ultimo sin con prossimo id
            upcolNext(idsin, _id)
            # detect repetition

            # inserisco nuovo sin se non esite 13/05/2018 rimosso hm
            if findS(story) == 0:
                if liv == 1:
                    idsin = collectiont.insert(
                        {"liv": liv, "start": 1, "story": story, "next": "", "sax": sax, "weight": 0})
                else:
                    idsin = collectiont.insert(
                        {"liv": liv, "start": 0, "story": story, "next": "", "sax": sax, "weight": 0})
            else:
                idsin = findS(story)
                collectiont.update_one(
                    {"_id": idsin},
                    {
                        "$inc": {
                            "weight": 1
                        }
                    }
                )
                if liv == 1:
                    collectiont.update_one(
                        {"_id": idsin},
                        {
                            "$inc": {
                                "start": 1
                            }
                        }
                    )

            findH(story_list, story, sax, liv)
            #             print("esiste")
        i += 1
    return "ok"

# repetition rule
def rrule(data):

    data = data.split("=")
    asw = []
    story = ''.join("=".join(str(x) for x in data))
    nstory2 = []
    # cerco sax corrente
    sax = nsax(data, 0)
    rows = collectionl.find(
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
            w,s,e =findWById(int(r))
            asw.append(str(w).strip())

    return asw


def bringLevelDown(data, liv):
    return data[:liv]



def shortMemory(now):
    return 0

'''
def interact(stri):
    stri = stri.decode()

    # split speak
    maxEndR=collectionw.find().sort('end',-1).limit(1)
    maxEnd=maxEndR[0]["end"]
   
    next = 0
    str1 = []
    aws = []
    stop = 2
    row = []
    i = 0
    i2 = 0
    hm = 0
    s1=0
    e=0
    words = stri.split()

    # liv = len(words)
    for word in words:
        liv = i
        if findW(word) == 0:
                    # trovo id associati alle parole se non c'è la inserisco
            collectionw.insert(
                {"_id": getNextSequence(db.counters, "nodeid"), "word": word, "start": 0, "end": 0})
        str1.append(str(findW(word)).strip())
        i = + 1

    str2 = list(str1)

    story = ''.join("=".join(str(x) for x in str1))
    rex = "^(" + story + ").*"
    rows = collectiont.find({"story": {'$regex': rex}})
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
        pprint("CICLO 0: BASE")
        str2.pop(-1)
        ls2 = ls2 - 1
        story = ''.join("=".join(str(x) for x in str2))
        if rc != 0 or ls2 == 0:
            # se non c'è nemmeno un collegamento vado di regola... non so se
            # fare il contrario

            stop = 1

            pprint("SKIP: stoppo con array "+str(str1))

    while(next != ""):

        pprint("Loop, stop:" + str(stop))
        if stop == 1:
            pprint("CICLO 1: Armonico")
            # cerco quindi in Logic una regola tipo 1=2=0 con campo wtd (what to do) che deve essere tipo [1,4] e vuol dire che quello che è nella pos 1 della
            # mia story lo metto anche nella posizione 4 della story finale
            # scritta nel campo fstory della regola
            try:
                aws = rrule(vartemp)
                pprint(len(aws))
                # no rule
                if len(aws) == 0:
                    pprint("IF")
                    # nessun risultato
                    # provo con la media armonica
                    #pprint("LISTA: "+str1)
                    story_list = [float(y) for y in str1]
                    
                    # media armonica
                    hm = harmonic_mean(story_list)
                    rows = findH2(story_list, hm, liv)
                    # pprint(liv)
                    # se cmq è ancora a 0
                    if rows.count() == 0:
                        pprint("NON PASSO A CICLO2")
                        next = ""
                    else:
                        pprint("PASSO A CICLO2")
                        i2 = -1
                        stop = 2 
                else:
                    pprint("NON 0")
            except:
                print("Unexpected error:", sys.exc_info()[0])
                pass


        elif stop == 2:
            # test: inizio con il primo e basta.
            pprint("CICLO 2:" + str(i2))
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
            rows = collectiont.find({"story": story})
            pprint("STORY: " + story)
            pprint("ARRAY: " + str(aws))
            #nn=row['next']
            #cerco il valore END dell'ultima parola della risposta creata
            wn=findWByIdFull(next)
            #end
            
            if wn!='':
                end=wn['end']
            #use fibonacci for calulate end value
            if i2>0:
                endMax=maxEnd/F(i2)
            else:
                endMax=999999

            pprint(str(endMax))
            if rows.count() == 0:
                next = ""
            
            pprint("ME: "+str(endMax)+" END "+str(end))
            if row['next'] == "" or end>endMax:
                next = ""
                # next = ""
             #   pprint("nores")



            #next = ""
            # fermo il ciclo

        i2 = i2 + 1
        answer = ' '.join(aws)
    return answer*/
'''
def interact(stri):
    stri = stri.decode()

    # split speak
    maxEndR=collectionw.find().sort('end',-1).limit(1)
    maxEnd=maxEndR[0]["end"]
    next = 0
    str1 = []
    aws = []
    stop = 0
    row = []
    i = 0
    i2 = 0
    hm = 0
    s1=0
    e=0
    words = stri.split()

    # liv = len(words)
    for word in words:
        liv = i
        if findW(word) == 0:
            # trovo id associati alle parole se non c'è la inserisco
            collectionw.insert(
                {"_id": getNextSequence(db.counters, "nodeid"), "word": word, "start": 0, "end": 0})
        str1.append(str(findW(word)).strip())
        i = + 1

    str2 = list(str1)
    if deb == 1:    
        pprint("coversion:"+str(str2))
    story = ''.join("=".join(str(x) for x in str1))

    #cerco story che INIZIANO con quella appena passata
    rex = "^(" + story + ").*"
    if deb == 1:    
        pprint (rex)

    rows = collectiont.find({"story": {'$regex': rex}})
    # pprint(str1)
    vartemp = story
    # se non ci sono risultati diminuisco di uno l'array
    # pprint(rows.count())
    # row count
    rc = rows.count()
    # len str2
   
    ls2 = len(str2)

    if rc == 0:
        stop = 0
    # non va x me

        # pprint("stoppo con array "+str(str1))

    while(next != ""):

        if stop == 0:
            if deb == 1:    
                pprint("meno uno")
            str2.pop(-1)
            ls2 = ls2 - 1

            story0 = ''.join("=".join(str(x) for x in str2))
            rex = "^(" + story0 + ").*"
            if deb == 1:    
                pprint("cerco" + str(str2))
            rows = collectiont.find({"story": {'$regex': rex}})
            rc = rows.count()

            if rc != 0:
                i2 = -1
                stop = 2
            elif ls2 == 0:
                next = ""

                #pprint("Loop, stop:" + str(stop))

        if stop == 1:
            if deb == 1:    
                pprint("ciclo armonico")
            # cerco quindi in Logic una regola tipo 1=2=0 con campo wtd (what to do) che deve essere tipo [1,4] e vuol dire che quello che è nella pos 1 della
            # mia story lo metto anche nella posizione 4 della story finale
            # scritta nel campo fstory della regola
            try:
                aws = rrule(vartemp)
                # pprint(len(aws))
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
                        stop = 2
                    else:
                        i2 = -1
                        stop = 2

            except:
                stop = 2
                pass
        if stop == 2:
            if deb == 1:    
                pprint("costruttore next")
            # test: inizio con il primo e basta.
            #pprint("inizio ciclo 2 con i2:" + str(i2))


            if i2 == 0:
                rex = "^(" + story + ").*"

                rows = collectiont.find({"story": {'$regex': rex}})
                if deb == 1:    
                    pprint("RIGHE RISULTATO"+str(rows.count()))
                row = rows[0]
                next = row['next']
                #if hm != 0:
                story = row['story']
                s2 = story.split("=")
                for s in s2:
                    s = int(s)
                    w1,s1,e =findWById(s)
                    aws.append(w1)
                w2,s1,e=findWById(next)
                aws.append(w2)


            else:
                if rows.count()!=0:
                    row = rows[0]
                    next = row['next']
                    for row in rows:
                        next = row['next']
                        w3,s1,e=findWById(next)
                        aws.append(w3)
                        if e>10:
                            next = ""
                            pprint ("ESCO")
                            break
                else:
                    pprint("PAROLA NON CONOSCIUTA")
                    aws.append("Non conosco questa parola")
                    next=""
                    answer = ' '.join(aws)
                    break


            # aggiorno la story per cercare il prossimo next
            story = story + '=' + str(next)
            rows = collectiont.find({"story": story}).sort(
                "weight", -1)  # per il peso
            
            if deb == 1:    
                pprint("STORY: " + story)
                pprint("ARRAY: " + str(aws))
            #nn=row['next']
            #cerco il valore END dell'ultima parola della risposta creata
            wn=findWByIdFull(next)
            #end
            
            if wn!='':
                end=wn['end']
            else:
                end=0
            #use fibonacci for calulate end value
            if i2>0:
                endMax=maxEnd/F(i2)
            else:
                endMax=999999

            if rows.count() == 0:
                next = ""
            
            if deb == 1:    
                pprint("ME: "+str(endMax)+" END "+str(end))

            if row['next'] == "" or end>endMax:
                next = ""

                # next = ""
             #   pprint("nores")



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
    return izip_longest(fillvalue=fillvalue, *args)


def splitBig(maxFile):
    import os
    for file in os.listdir("./train/file"):
        if file.endswith(".txt"):
            path=os.path.join("./train/file", file)
            pprint(path)
            rangeC = 1
            rangeC = rawbigcount(path)
            # sempre numero intero
            while rangeC % maxFile == 0:
                rangeC = rangeC + 1
            
            n = (rangeC / maxFile)
        
            with open(path) as f:
                for i, g in enumerate(grouper(n, f, fillvalue=''), 0):
                    with open('./train/new/small_file_{0}.txt'.format(i), 'w') as fout:
                        fout.writelines(g)


def train(index):
    pprint("ok")
    # cerco se ci sono dei progressi
    #
    progFile = "./train/new/progress{0}.txt".format(index)
    trainFileDone = "./train/done/small_file_{0}.txt".format(index)
    trainFile = "./train/new/small_file_{0}.txt".format(index)

    #pprint("current file: "+trainFile)

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

    

    files = io.open(trainFile, "r", encoding="utf8")
    files= files.read().replace("\n"," ").replace( "\r"," ")
    remove = string.punctuation
    remove = remove.replace("-", "")
    remove = remove.replace(",", "")
    remove = remove.replace("%", "")
    remove = remove.replace("&", "")
    remove = remove.replace("#", "")
    remove = remove.replace("/", "")
    remove = remove.replace(":", "")
    remove = remove.replace("-", "")
    remove = remove.replace("'", "")

    file=re.split('['+remove+']', files)
     # don't remove hyphens
    rangeC = len(file)
    str1 = ""


    filex = open(progFile, "w")
    os.rename(trainFile, trainFileDone)
    non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)

    # progressbar usage
    for line in file:
        line = line.replace("\n", "")
        '''
        if i % 2 == 0:
            str1 = line.translate(non_bmp_map)
        else:
            str2 = line.translate(non_bmp_map)
        '''
        str1 = line.translate(non_bmp_map)
        trainAI(str1)
        filex.seek(0)
        filex.truncate()
        filex.write(str(i))
        sys.stdout.write("\rProgress:" + str(i) + "/" + str(rangeC))
        sys.stdout.flush()

        i += 1

def averEnd():
    avg=collectionw.aggregate([{ "$match": {"end": { "$gt": 0 }}},{ "$group": { "_id": 'null',"end": { "$avg": "$end" },"start": { "$avg": "$start" }}}])
    ind=0
    aaa=[]
    for row in avg:
        ind += 1
        aaa.append(row["start"])
        aaa.append(row["end"])
    return aaa

# Return CPU temperature as a character string      


def getCPUtemperature():
    res =  os.popen('sensors | grep "temp1:" | cut -d+ -f2 | cut -c1-2').read()
    return res

# Return % of CPU used by user as a character string                                
def getCPUuse():
    return(str(os.popen("top -n1 | awk '/Cpu\(s\):/ {print $2}'").readline().strip(\
)))

def dna():
    a = findGen('dna')
    if(a==0):
        hexdigits = "0123456789ABCDEF"
        random_digits = "".join([ hexdigits[random.randint(0,0xF)] for _ in range(16) ])
        dna = collectionm.insert(
                        {"dna": random_digits, "date": time.strftime("%d/%m/%Y")})
    else:
        random_digits=a

    return random_digits

def humor():
    data=[]
    busy=getCPUuse()
    temperature=getCPUtemperature()
    data.append(busy)
  #  data.append(temperature)
    return data


def getInput():
    #load?
    aver=averEnd()
    im=humor()
    pprint("Averange Start: "+str(aver[0]));
    pprint("Averange End: "+str(aver[1]));
    pprint("Busy: "+str(im[0]));
    pprint("DNA: "+str(dna()));
 #   pprint("Temperature: "+str(im[1]));
    while(0 == 0):
        text = raw_input("Please enter something: ")
        s = interact(text)
        print(s)
import multiprocessing
maxProcess =multiprocessing.cpu_count() 

# multiprocessing trainig


def conn():

    #conn.db = MongoClient('mongodb://nuked:112358@192.168.1.3:27017/?authMechanism=DEFAULT&authSource=morphit')
    # conn.db = MongoClient('192.168.1.3').morphit
    # conn.db.authenticate('nuked', '112358', mechanism='SCRAM-SHA-1')
    # conn.collectionw = conn.db['words']
    ## conn.collectiont = conn.db['sinMemo']
    # conn.collectionl = conn.db['sinLogic']
    pass


def f(i):
    my_i = []
    splitBig(maxProcess)

    for count in range (0,maxProcess):
        my_i.append(count)

    # make the Pool of workers
    pool = ThreadPool(maxProcess) 
    results = pool.map(train, my_i)
    print results

    pool.close() 
    pool.join() 


def main(argv):
    pprint(str(argv))
    try:
        opts = argv
    except getopt.GetoptError:
        print 'test.py -t <numero file train>'
        sys.exit(2)
  
    if opts[0] == '-h':
        print 'test.py -t <numero file train>'
        sys.exit()
    elif opts[0] =='-t':
        pprint(opts[1])
        f(int(opts[1]))
    elif opts[0] =='-i':
        getInput()





if __name__ == '__main__':
    pprint("Start")
    main(sys.argv[1:])
    # getInput()

    #p = Pool(maxProcess)
    #print(p.map(f, [1, 2]))

    #
    # text = "ciao sono A151edo"

    # train()
    # s = trainAI(text)

    # print s

            