def predict_pre_post(clf, question, minimum_confidence):
    confidence = clf.predict_proba([question])
    postpaid_confidence = confidence[0][0]
    prepaid_confidence = confidence[0][1]
    #print("prepaid confidence: " + str(prepaid_confidence))
    #print("postpaid confidence: " + str(postpaid_confidence))
    if prepaid_confidence > minimum_confidence:
        return "prepaid"
    elif postpaid_confidence > minimum_confidence:
        return "postpaid"
    else:
        return "unknown"

def predict_web_com(sess, question, minimum_confidence):
    graph = sess.graph
    x_data = graph.get_tensor_by_name("x_data:0")
    probability = graph.get_tensor_by_name("probability:0")
    confidence = sess.run(probability, feed_dict={x_data: question.todense()})[0][0]
    community_confidence = 1 - confidence
    website_confidence = confidence
    #print(type(community_confidence))
    #print("website confidence: " + str(website_confidence))
    #print("community confidence: " + str(community_confidence))
    if website_confidence > minimum_confidence:
        return "website"
    elif community_confidence > minimum_confidence:
        return "community"
    else:
        return "unknown"
