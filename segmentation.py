import os
import glob
import re
from collections import namedtuple
from bs4 import BeautifulSoup as BS

from eleve import MemoryStorage as Storage
from eleve import Segmenter

def loadRaw():
    corpus = []
    for f in glob.glob("./hackpad-backup-g0v/*.html"):
        page_id = f.rsplit("/",1)[-1][:-5]
        print(page_id)
        url = "https://g0v.hackpad.com/%s.html" % (page_id,)
        with open(f) as F:
            html = open(f).read()
            bs = BS(html)
            title = next(bs.body.children).text
            print(title)
            body = bs.body.text
            corpus.append((page_id, body))
    return corpus

def trainSegmenter(corpus):
    storage = Storage(6)
    for page_id, pad in corpus:
        for line in pad.split("\n"):
            storage.add_sentence(list(line.strip()))
    return storage

def segmenteCorpus(corpus, storage):
    result = []
    seg = Segmenter(storage)
    for page_id, pad in corpus:
        for line in pad.split("\n"):
            result.extend(["".join(w) for w in seg.segment(list(line))])
    return result



