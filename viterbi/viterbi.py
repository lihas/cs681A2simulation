__author__ = 'lihas'
import os

class sentence_word:
    word=""
    back_pointer=0


class viterbi(object):

    __corpus=""
    __corpus_contents=[] #each element of this list will contain a token from the corpus
    corpus_sanitized="corpus_sanitized"
    transition_matrix_count={} #transition_matrix_count and emission_matrix_count store only corresponding counts and not probabilities
    emission_matrix_count={}
    transition_matrix_prob={} #transition_matrix_prob and emission_matrix_prob store only corresponding probabilities
    emission_matrix_prob={}

    def __init__(self,corp):
        self.corpus=corp

    #corpus file
    @property
    def corpus(self):
        if(self.__corpus==""):
            print("Error! corpus not set")
            return False
        return self.__corpus

    @corpus.setter
    def corpus(self,file):
        self.__corpus=file

    #return tag
    def getTag(self,word1):
        return word1.split("_")[1]

    def init_matrix_count(self):
        """
            initialises transition_matrix_count and emission_matrix_count with counts from corpus
            note that these matrices don't store probabilities, they just have counts

        :return: False in case of error else nothing
        """
        if not self.corpus :
            print("Error! viterbi::transition_matrix")
            return False

        file_corpus=open(self.corpus,'r')
        file_corpus_contents=file_corpus.readline().split()
        self.__corpus_contents=file_corpus_contents
         #initialize transition
        word1=file_corpus_contents[0]
        self.transition_matrix_count["^"]={}
        self.transition_matrix_count["^"][self.getTag(word1)]=1
        self.addEmissionEntry(word1)

        for word2 in file_corpus_contents[1:]:
            self.addTransitionEntry(word1,word2)
            self.addEmissionEntry(word2)
            word1=word2

    def calculate_probability(self):
        self.emission_matrix_prob=self.emission_matrix_count.copy()
        self.emission_matrix_prob=self.transition_matrix_count.copy()
        for i in self.emission_matrix_prob:
            rowsum=0
            for j in self.emission_matrix_prob[i]:
                rowsum+=self.emission_matrix_prob[i][j]
            for j in self.emission_matrix_prob[i]:
                self.emission_matrix_prob/=rowsum
        for i in self.transition_matrix_prob:
            rowsum=0
            for j in self.transition_matrix_prob[i]:
                rowsum+=self.transition_matrix_prob[i][j]
            for j in self.transition_matrix_prob[i]:
                self.transition_matrix_prob/=rowsum

    def run_Viterbi(self,sentence):
        sentence_words=sentence.split()
        for i in range(len(sentence_words)):
            sentence_word_temp=sentence_words()
            sentence_word_temp.word=sentence_words[i]
            sentence_dict={i:sentence_word_temp}

    def getTag(self,word1): #return tag
        return word1.split("_")[1]

    def getDictionaryValue(self,dictionary, i, j):
        __doc__ = "by default returns zero for missing dictionary items"
        if i in dictionary:
            if j in dictionary[i]:
                return dictionary[i][j]
            else:
                return 0;
        else:
            print("error: wasn't expecting this!!! "+i)

    def addEmissionEntry(self,word1):
        split1=word1.split("_")
        word_main=split1[0]
        word_tag=split1[1]

        if word_tag in self.emission_matrix_count:
            if word_main in self.emission_matrix_count[word_tag]:
                self.emission_matrix_count[word_tag][word_main]+=1
            else:
                self.emission_matrix_count[word_tag][word_main]=1
        else:
            self.emission_matrix_count[word_tag]={}
            self.emission_matrix_count[word_tag][word_main]=1



    def addTransitionEntry(self,word1, word2):
        tag1=self.getTag(word1)
        tag2=self.getTag(word2)
        if tag1=="_.":
                tag1="^"

        if tag1 in self.transition_matrix_count:
            if tag2 in self.transition_matrix_count[tag1]:
                self.transition_matrix_count[tag1][tag2]+=1
            else:
                self.transition_matrix_count[tag1][tag2]=1
        else:
            self.transition_matrix_count[tag1]={}
            self.transition_matrix_count[tag1][tag2]=1


    def sanitize_corpus_double(self):
        if not self.corpus:
            print("error! sanitize_corpus_double")
            return False
        raise NotImplementedError
        #inefficiecnt code
        # file_corpus=open(self.corpus,'r')
        # file_corpus_contents=file_corpus.readline().split()
        # file_corpus_sanitize=open(self.corpus_sanitized,'w')
        # word1=file_corpus_contents[0]
        # for word2 in file_corpus_contents[1:]:
        #     if



x=viterbi("brown.txt")
#x.corpus="brown.txt"
x.init_matrix_count()

