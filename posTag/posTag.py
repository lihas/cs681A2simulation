import json
__author__ = 'neo'
corpus=open("brown2.txt","r")
tr=open("tr.json","w")
em=open("em.json","w")
transition={} #transition table
emission={} #emission table


#line=tagfile.readline()
#line=line.rstrip('\n')
#transition[line]={}

def getTag(word): #return tag
    return word.split("_")[1]


def addEmissionEntry(word):
    split1=word.split("_")
    word_main=split1[0]
    word_tag=split1[1]
    if word_main in emission:
        if word_tag in emission[word_main]:
            emission[word_main][word_tag]+=1
        else:
            emission[word_main][word_tag]=1
    else:
        emission[word_main]={}
        emission[word_main][word_tag]=1




def addTransitionEntry(word1, word2):
    tag1=getTag(word1)
    tag2=getTag(word2)
    if tag1=="_.":
        tag1="^"

    if tag1 in transition:
        if tag2 in transition[tag1]:
            transition[tag1][tag2]+=1
        else:
            transition[tag1][tag2]=1
    else:
        transition[tag1]={}
        transition[tag1][tag2]=1


word1=corpus.readline().rstrip('\n')
transition["^"]={}
transition["^"][getTag(word1)]=1
addEmissionEntry(word1)




for word2 in corpus:
    word2=word2.rstrip("\n")
    addTransitionEntry(word1,word2)
    addEmissionEntry(word2)
    word1=word2
    #print(word1,"#",word2,"\n")

json.dump(transition,tr)
json.dump(emission,em)
#print(transition["WPS+BEZ-NC"]["PPS-NC"])