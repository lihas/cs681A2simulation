import nltk
from nltk.stem import WordNetLemmatizer
from nltk.stem import PorterStemmer
wn=WordNetLemmatizer()
porter=PorterStemmer()
porter_stemmer=PorterStemmer()
lmtzr=WordNetLemmatizer()
#x=wn.lemmatize('car',) 'a',n,v,r:adverb
testno='2';

"""
to use wordnet.ADJ type syntax:
from nltk.corpus import wordnet
wornet.ADJ

"""


#corpus=open('brown.txt','r')
output=open('brown2.txt','w')
result=output
#content_corpus=corpus.readline()
#tag_set={'NN':'n','NN$':'n','NNS':'n','NNS$':'n','NP':'n','NP$':'n','NPS':'n','NPS$':'n','NR':'n','VB':'v','VBD':'v','VBG':'v','VBN':'v','VBP':'v','VBZ':'v','RB':'r','RBR':'r','RBT':'r','RN':'r','RP':'r','JJ':'a','JJR':'a','JJS':'a','JJT':'a'}.get(x,'n')

def wordnet_pos(word):
        w=word
        spl=w.split("_")
        if(spl.__len__()<2):
            return
        word=spl[0]
        tag=spl[1]
        if tag.startswith('N'):
            pos='n'
        elif tag.startswith('V'):
            pos='v'
        elif tag.startswith('R'):
            pos='r'
        elif tag.startswith('J'):
            pos='a'
        else:
            return 0
        return pos
        #lemma=wn.lemmatize(word)
        #stem=porter.stem(word)
        #output.write(lemma+'_'+tag+' ')
        #output.write(stem+'_'+tag+' ')

#apoorv
import os.path

def getSuffix(lemma,word):
    if lemma==word:
        return 0;
    if word.endswith('ing'):
        return 'ing'
    if word.endswith('en'):
        return 'en'
    if word.endswith('ed'):
        return 'ed'
    if word.endswith('ist'):
        return 'ist'
    if word.endswith('est'):
        return 'est'
    if word.endswith('able'):
        return 'able'
    if word.endswith('ful'):
        return 'ful'
    if word.endswith('ly'):
        return 'ly'
    if word.endswith('ise'):
        return 'ise'
    if word.endswith('ize'):
        return 'ize'
    if word.endswith('fy'):
        return 'fy'
    if word.endswith('hood'):
        return 'hood'
    if word.endswith('n\'t'):
        return 'n\'t'
    if word.endswith('er'):
        return 'er'
    if word.endswith('ness'):
        return 'ness'
    if word.endswith('less'):
        return 'less'
    if word.endswith('ism'):
        return 'ism'
    if word.endswith('ment'):
        return 'ment'
    if word.endswith('tion'):
        return 'tion'
    if word.endswith('ology'):
        return 'ology'
    if word.endswith('ess'):
        return 'ess'
    if word.endswith('al'):
        return 'al'
    if word.endswith('ish'):
        return 'ish'
    if word.endswith('t'):
        return 't'
    else:
        root = os.path.commonprefix([lemma,word])
        length = len(root)
        wordlen = len(word)
        return word[length:wordlen]


#apoorv

with open('brown.txt','r') as f:
    for line in f:
        for word in line.split():
            list=word.split("_")
            stem=porter_stemmer.stem(list[0])
            if list[0]==stem:
                result.write(list[0]+"_"+list[1]+" ")
            else:
                pos=wordnet_pos(word)
                if not pos:
                    result.write(list[0]+"_"+list[1]+" ")
                else:
                    lemma1=lmtzr.lemmatize(list[0],pos)
                    result.write(lemma1+"_"+list[1]+" ")
                    suffix=getSuffix(lemma1,list[0])
                    if not suffix:
                        continue
                    else:
                        result.write(suffix+"_"+suffix.upper()+" ")



