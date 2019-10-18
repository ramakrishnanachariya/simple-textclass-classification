import nltk
from nltk.stem.lancaster import LancasterStemmer
import numpy as np
import tflearn
import tensorflow as tf
import random
import json
import string
import unicodedata
import sys

# a table structure to hold the different punctuation used
tbl = dict.fromkeys(i for i in xrange(sys.maxunicode)
                      if unicodedata.category(unichr(i)).startswith('P'))

# method to remove punctuations from sentences.
def remove_punctuation(text):
    return text.translate(tbl)

#initialize the stemmer
stemmer = LancasterStemmer()
#variable to hold the Json data read from the file
data = None

# read the json file and load the training data
with open('data.json') as json_data:
    data = json.load(json_data)
    print (data)

# get a list of all categories to train for
categories = list(data.keys())
words = []
# a list of tuples with words in the sentence and category name 
docs = []

for each_category in data.keys():
    for each_sentence in data[each_category]: 
        # remove any punctuation from the sentence
	each_sentence = remove_punctuation(each_sentence)
	print each_sentence
        # extract words from each sentence and append to the word list
        w = nltk.word_tokenize(each_sentence)
	print "tokenized words: ", w
        words.extend(w)
        docs.append((w, each_category))

# stem and lower each word and remove duplicates
words = [stemmer.stem(w.lower()) for w in words]
words = sorted(list(set(words)))

print (words)
print (docs)

# create our training data
training = []
output = []
# create an empty array for our output
output_empty = [0] * len(categories)


for doc in docs:
    # initialize our bag of words(bow) for each document in the list
    bow = []
    # list of tokenized words for the pattern
    token_words = doc[0]
    # stem each word
    token_words = [stemmer.stem(word.lower()) for word in token_words]
    # create our bag of words array
    for w in words:
        bow.append(1) if w in token_words else bow.append(0)
    
    output_row = list(output_empty)
    output_row[categories.index(doc[1])] = 1
    
    training.append([bow, output_row])

random.shuffle(training)
training = np.array(training)

train_x = list(training[:,0])
train_y = list(training[:,1])

tf.reset_default_graph()
net = tflearn.input_data(shape=[None, len(train_x[0])])
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, len(train_y[0]), activation='softmax')
net = tflearn.regression(net)

model = tflearn.DNN(net, tensorboard_dir='tflearn_logs')
model.fit(train_x, train_y, n_epoch=1000, batch_size=8, show_metric=True)
model.save('model.tflearn')


# let's test the mdodel for a few sentences:
# the first two sentences are used for training, and the last two sentences are not present in the training data. 
sent_1 = "what time is it?"
sent_2 = "I gotta go now"
sent_3 = "do you know the time now?"
sent_4 = "you must be a couple of years older then her!"

def get_tf_record(sentence):
    global words
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [stemmer.stem(word.lower()) for word in sentence_words]
    bow = [0]*len(words)  
    for s in sentence_words:
        for i,w in enumerate(words):
            if w == s: 
                bow[i] = 1

    return(np.array(bow))



print( categories[np.argmax(model.predict([get_tf_record(sent_1)]))])
print( categories[np.argmax(model.predict([get_tf_record(sent_2)]))])
print( categories[np.argmax(model.predict([get_tf_record(sent_3)]))])
print( categories[np.argmax(model.predict([get_tf_record(sent_4)]))])




