__author__ = 'neo'
import json
file1="file1.txt"
file2="file2.txt"
f1 = open(file1, "r")
f2 = open(file2, "r")
cn = open("cn.json", "w")
xl_confusion = open("xl_confusion.xls", "w")
xl_performanceParameters=open("xl_performanceParameters.xls","w")
confusion = {}


def getTag(word):  # return tag
    return word.split("_")[1]


def addConfusion(tag1, tag2):
    if tag1 in confusion:
        if tag2 in confusion[tag1]:
            confusion[tag1][tag2] += 1
        else:
            confusion[tag1][tag2] = 1
    else:
        confusion[tag1] = {}
        confusion[tag1][tag2] = 1


for word1 in f1:
    word1 = word1.rstrip("\n")
    word2 = f2.readline().rstrip("\n")
    # if word_main1!=word_main2:
    #     input()
    #     print("words dont match",word1,word2)
    tag1 = getTag(word1)
    tag2 = getTag(word2)
    addConfusion(tag1, tag2)


taglist = confusion.keys()
print(len(taglist))
taglist_column=list(taglist)

for i in taglist:
    for j in confusion[i]:
        if j not in taglist_column:
            taglist_column.append(j)


temp=open("temmp.txt","w")
for k in taglist_column:
    temp.write(k+"\n")

def getDictionaryValue(dictionary, i, j):
    __doc__ = "by default returns zero for missing dictionary items"
    if i in dictionary:
        if j in dictionary[i]:
            return dictionary[i][j]
        else:
            return 0;
    else:
        print("error: wasn't expecting this!!! "+i)

# excel file (tab separated)
print(len(taglist))
xl_confusion.write("#")
for i in taglist_column:
    xl_confusion.write("\t")
    xl_confusion.write(i)


for i in taglist:
    xl_confusion.write("\n")
    xl_confusion.write(i)
    xl_confusion.write("\t")
    for j in taglist_column:
        xl_confusion.write(str(getDictionaryValue(confusion,i,j)))
        xl_confusion.write("\t")
xl_confusion.close()

#excel file ends. excel file created!!!

#now calculating performance attributes

#recall

recallDictionary={} #will store recall values of tags
#calculating precision,recall,f-score
print("recall")
print(len(taglist),len(taglist_column))
for i in taglist:
    rowSum = 0
    recall=0
    #print(i)
    for j in taglist_column:
        rowSum += getDictionaryValue(confusion,i,j)
    #print("rowsum"+i)
    tp=getDictionaryValue(confusion,i,i) #true positive
    recall=tp/rowSum
    recallDictionary[i]=recall

#precision
print("precision")
precisionDictionary={}
for i in taglist:
    columnSum=0
    precision=0
    for j in taglist:
        columnSum+=getDictionaryValue(confusion,j,i)
    tp=getDictionaryValue(confusion,i,i)
    if columnSum==0:
        precision=0
    else:
        precision=tp/columnSum
    precisionDictionary[i]=precision

#f-scores
fscoreDictionary={}
for i in taglist:
    pr=precisionDictionary[i]
    rc=recallDictionary[i]
    if(pr==0 and rc==0):
        fscoreDictionary[i]=0
    else:
        fscoreDictionary[i]=2*pr*rc/(pr+rc)

#creating excel for performance parameters

xl_performanceParameters.write(" ")
xl_performanceParameters.write("\t")
xl_performanceParameters.write("recall\tprecision\tf-score\n")
for i in taglist:
    xl_performanceParameters.write(i)
    xl_performanceParameters.write("\t")
    xl_performanceParameters.write(str(recallDictionary[i]))
    xl_performanceParameters.write("\t")
    xl_performanceParameters.write(str(precisionDictionary[i]))
    xl_performanceParameters.write("\t")
    xl_performanceParameters.write(str(fscoreDictionary[i]))
    xl_performanceParameters.write("\n")
xl_performanceParameters.close()
#performance parameters excel file created

digsum=0
for i in taglist:
    digsum+=getDictionaryValue(confusion,i,i)

tot_sum=0
for i in taglist:
    for j in taglist_column:
        tot_sum+=getDictionaryValue(confusion,i,j)
import pdb
#pdb.set_trace()
print(" % Accuracy :",digsum/tot_sum,digsum,tot_sum)