__author__ = 'neo'
import nltk
import sys
import os
sentence="is_BEZ also_RB not_NOT doing_VBG".split()
sentence_length=len(sentence)

grammar=nltk.data.load("file:cfg_rules.cfg")
grammar_dict={}
for i in grammar.productions():
    prod='##'
    for j in i.rhs():
        prod+=str(j)+'##'
    grammar_dict[prod]=str(i.lhs())

#def getRhsProd(v1,v2):
#    for i in grammar.productions():
#        if v1 in i.rhs() and v2 in i.rhs():
#            return i.lhs()
#        else:
#            return 0
#
def getRhsProd(v1,v2):
    x1='##'+v1+'##'+v2+'##'
    x2='##'+v2+'##'+v1+'##'
    print(x1);
    if x1 in grammar_dict.keys():
        return grammar_dict[x1]
    elif x2 in grammar_dict.keys():
        return  grammar_dict[x2]
    else:
        return False;


list_2d=[['' for i in range(sentence_length)] for j in range(sentence_length)]
list_2d_coords=[[-1 for i in range(sentence_length)] for j in range(sentence_length)]
for i in range(0,sentence_length):
    list_2d[i][i]=sentence[i].split('_')[1]
    list_2d_coords[i][i]=0;#tracking diagonal elements
    for j in range(i-1,-1,-1):
        kk=-1;
        for k in range(j+1,i+1):
            #pr=getRhsProd(list_2d[k][i],list_2d[j][kk+j])
            kk+=1;
            pr=getRhsProd(list_2d[i][k],list_2d[kk+j][j])
            if pr:
                list_2d[i][j]=pr;
                list_2d_coords[i][j]=[[i,k],[kk+j,j]]

#for i in list_2d:
#    print('\n')
#    for j in i:
#        print(j)

#   print("sahilllll")
#print(list_2d[sentence_length-1][0])



prin=sys.stdout.write

def printTree(i,j):
    if list_2d_coords[i][j]==-1:
        return ''
    if list_2d_coords[i][j]==0:
        prin(list_2d[i][j])
        prin(" "+sentence[i].split('_')[0])
        return
    prin(list_2d[i][j])
    prin("(")
    printTree(list_2d_coords[i][j][1][0],list_2d_coords[i][j][1][1])
    prin(")")
    prin("(")
    printTree(list_2d_coords[i][j][0][0],list_2d_coords[i][j][0][1])
    prin(")")

printTree(sentence_length-1,0);