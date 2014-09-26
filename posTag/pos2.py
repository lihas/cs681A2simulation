import json
__author__ = 'neo'
corpus=open("brown2.txt","r")
outfile=open("out.txt","w")
transition={} #transition table
emission={} #emission table


#line=tagfile.readline()
#line=line.rstrip('\n')
#transition[line]={}

def getTag(word): #return tag
    return word.split("_")[1]


def addTransitionEntry(word1, word2):
    tag1=getTag(word1)
    tag2=getTag(word2)
    if tag1=="_.":
        tag1="^"

    if tag1 in transition:
        if tag2 in transition[tag1]:
            temp_var= transition[tag1][tag2]
            temp_var+=1
            transition[tag1][tag2]=temp_var
        else:
            transition[tag1][tag2]=1
    else:
        transition[tag1]={}
        transition[tag1][tag2]={}


word1=corpus.readline().rstrip('\n')
transition["^"]={}
transition["^"][getTag(word1)]=1




for word2 in corpus:
    addTransitionEntry(word1,word2)
    word1=word2

json.dump(transition,outfile)

