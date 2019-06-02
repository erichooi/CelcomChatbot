import pickle
import tensorflow as tf
import nltk
import string

tfidf = pickle.load(open("tfidf.pickle", "rb"))


def tokenizer(text):
    text = nltk.word_tokenize(text)
    return text

def clean_question(text):
    text = text.lower()
    text = "".join(c for c in text if c not in string.punctuation)
    text = text.strip()
    return text

print("0. community\n1. website")
#tf_model = input("Enter the model filename: ")
tf_model = "model.ckpt.meta"
question = input("Enter your question: ")
question = clean_question(question)
question = tfidf.transform([question])
with tf.Session() as sess:
    saver = tf.train.import_meta_graph(tf_model)
    saver.restore(sess, tf.train.latest_checkpoint('./'))
    graph = sess.graph
    x_data = graph.get_tensor_by_name("x_data:0")
    probability = graph.get_tensor_by_name("probability:0")
    predict = graph.get_tensor_by_name("predict:0")
    probability = sess.run(probability, feed_dict={x_data: question.todense()})
    predict = sess.run(predict, feed_dict={x_data: question.todense()})
    if predict == 0:
        print("label is community")
        print("community probalility: " + str(1 - probability[0][0]))
        print("website probability: " + str(probability[0][0]))
    elif predict == 1:
        print("label is website")
        print("community probalility: " + str(1 - probability[0][0]))
        print("website probability: " + str(probability[0][0]))
