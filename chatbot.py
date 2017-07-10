#!/usr/bin/env python

from __future__ import print_function

from future.standard_library import install_aliases

install_aliases()

import json
import os
import csv

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)

#required webhook code
@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = processRequest(req)

    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

#checks the request to see if it is valid - outputs nothing if no request action is found
def processRequest(req):
    if req.get("result").get("action") != "list" and req.get("result").get("action") != "getWelcome" \
            and req.get("result").get("action") != "welcomeAnswer" \
            and req.get("result").get("action") != "getFilterAnswer" \
            and req.get("result").get("action") != "getTimeFilterAnswer" \
            and req.get("result").get("action") != "getKpiFilterAnswer" \
            and req.get("result").get("action") != "getSubjectFilterAnswer" \
            and req.get("result").get("action") != "getPassword" \
            and req.get("result").get("action") != "passwordWelcome":
        return {}

    if req.get("result").get("action") == "list":
        res = makeWebhookResult(req)
    elif req.get("result").get("action") == "passwordWelcome":
        res = getPasswordWebhook(req)
    elif req.get("result").get("action") == "getPassword":
        res = processPassword(req)
    elif req.get("result").get("action") == "welcomeAnswer":
        res = getWelcomeAnswerWebhook(req)
    elif req.get("result").get("action") == "getFilterAnswer":
        res = getFilterAnswerWebhook(req)
    elif req.get("result").get("action") == "getTimeFilterAnswer":
        res = getTimeFilterAnswerWebhook(req)
    elif req.get("result").get("action") == "getKpiFilterAnswer":
        res = getKpiFilterAnswer(req)
    elif req.get("result").get("action") == "getSubjectFilterAnswer":
        res = getSubjectFilterAnswerWebhook(req)
    else:
        res = getWelcomeWebhook(req)

    return res

def getPasswordWebhook(req):
    result = req.get("result")
    action = result.get("action")
    if action == "passwordWelcome":
        speech = "Hi! This is the CapcoBot. Please enter your password."
    else:
        speech = "Sorry, I couldn't understand your sentence."

    return returnStatement(speech)

def processPassword(req):
    result = req.get("result")
    parameters = result.get("parameters")
    password = parameters.get("password")
    with open('Data/passwords.csv', 'rb') as csvfile:
        my_content = csv.reader(csvfile, delimiter=',')
        for row in my_content:
            if password in row:
                speech = "You have been granted access."
            else:
                speech = "Incorrect password."

    return returnStatement(speech)


#calls checkForError to output the result
def makeWebhookResult(req):
    result = req.get("result")
    parameters = result.get("parameters")
    kpi = parameters.get("kpi")
    timeframe = parameters.get("timeframe")
    subject = parameters.get("subject")
    kpitype = parameters.get("kpi-type")

    speech = checkForError(kpi, kpitype, timeframe, subject)

    return returnStatement(speech)

#main return statement
def returnStatement(speech):
    return {
        "speech": speech,
        "displayText": speech,
        "data": {},
        "contextOut": [],
        "source": "chatbot"
    }

#takes in all significant parameters - this is where the actual results would be outputted
def checkForError(kpi, kpitype, timeframe, subject):
    historicalKPI = ['acquisition cost', 'current value', 'retention cost', 'product processing cost',
                     'purchase frequency',
                     'period since last purchase', 'non-interest revenue', 'interest revenue', 'product servicing fee']
    predictiveKPI = ['future value', 'customer lifetime value', 'referral/word of mouth value',
                     'customers with the highest probability to churn',
                     'customers with the highest probability to upsell/cross-sell',
                     'customers with the highest referral/word of mouth value',
                     'customers with the longest predicted lifetime duration',
                     'churn rate', 'lifetime duration']
    historicalTimeframe = ['past month', 'past week', 'today', 'past year', 'beginning of time']
    hkpi = False
    pkpi = False
    bkpi = False
    ht = False
    pt = False
    if kpi in historicalKPI:
        hkpi = True
    elif kpi in predictiveKPI:
        pkpi = True
    else:
        bkpi = True
    if timeframe in historicalTimeframe:
        ht = True
    else:
        pt = True
    if not (kpi or kpitype or timeframe or subject):
        speech = "I didn't quite understand that. Are you interested in customers, segments, enterprises, or products?"
    elif (subject == "customer" or subject == "product") and kpitype:
        speech = "This is an invalid statement. You cannot see the " + kpitype + " " + kpi + " for a " + subject
    elif pt and hkpi:
        speech = "This is an invalid statement. You cannot get predictive results for this statistic."
    elif ht and pkpi:
        speech = "This is an invalid statement. You cannot get historical results for this statistic."
    elif subject == "product" and ht and \
            (
                                    kpi != "product processing cost" or kpi != "purchase frequency"
                        or kpi != "product servicing fee" or kpi != "non-interest revenue"):
        speech = "This is an invalid statement. Are you interested in products?"
    elif subject == "product" and pt and pkpi != "churn rate":
        speech = "This is an invalid statement. Are you interested in statistics about products?"
    elif (subject == "enterprise" or subject == "segment") and ht and bkpi and not hkpi:
        speech = "This is an invalid statement. Are you interested in statistics about " + subject + "?"
    elif (subject == "enterprise" or subject == "segment") and ht and ((kpi != "purchase frequency" or
                                                                                kpi != "period since last purchase" or
                                                                                kpi != "product servicing frequency")) \
            and not kpitype:
        speech = "Would you like to know the average results or the sum results?"
    elif (subject == "enterprise" or subject == "segment") and pt and (
            (kpi != 'customers with the highest probability to churn' or
                     kpi != 'customers with the highest probability to upsell/cross-sell' or
                     kpi != 'customers with the highest referral/word of mouth value'
             or kpi != 'customers with the longest predicted lifetime duration')) and not kpitype:
        speech = "Would you like to know the average results or the sum results?"
    elif (subject == "enterprise" or subject == "segment") and ht and kpitype and \
            (kpi == "purchase frequency" or
                     kpi == "period since last purchase" or kpi == "product servicing frequency"):
        speech = "This is an invalid statement. Are you interested in statistics about " + subject + "?"
    elif (subject == "enterprise" or subject == "segment") and pt and \
            (kpi != "future value" or kpi != "customer lifetime value" or
                     kpi != "churn rate" or kpi != "lifetime duration" or kpi != "referral/word of mouth value"):
        speech = "This is an invalid statement. Are you interested in statistics about " + subject + "?"
    elif (subject == "enterprise" or subject == "segment") and \
            pt and kpitype and (kpi == "churn rate" or kpi == "lifetime duration"):
        speech = "This is an invalid statement. Are you interested in statistics about " + subject + "?"
    else:
        if kpitype:
            speech = "Here is the list for the " + kpitype + " " + kpi + " for each " + subject + " for the " + \
                     timeframe + ":"
        elif kpi == "most profitable customers" or kpi == "least profitable customers":
            speech = "Here is the list for the " + kpi + " for the " + timeframe
        else:
            speech = "Here is the list for the " + kpi + " for each " + subject + " for the " + timeframe + ":"

    print("Response:")
    print(speech)

    return speech

#welcoming intent
def getWelcomeWebhook(req):
    result = req.get("result")
    action = result.get("action")
    if action == "getWelcome":
        speech = "Hi! This is the CapcoBot. Please enter your question, or type 'filter' for more options."
    else:
        speech = "Sorry, I couldn't understand your sentence."

    return returnStatement(speech)

#determines whether you type 'filter' or your query
def getWelcomeAnswerWebhook(req):
    result = req.get("result")
    parameters = result.get("parameters")
    filter = parameters.get("filter")
    kpi = parameters.get("kpi")
    timeframe = parameters.get("timeframe")
    subject = parameters.get("subject")
    kpitype = parameters.get("kpi-type")
    if (filter and kpi and kpitype and subject and timeframe) or \
            (kpi and kpitype and subject and timeframe) or \
            (kpi and timeframe and (subject == "customer" or subject == "product")):
        speech = "Awesome! I have all the information I need. " + checkForError(kpi, kpitype, timeframe, subject)
    elif filter and not (kpi or kpitype or subject or timeframe):
        speech = "Let's get started! Are you interested in historical or predictive data?"
    else:
        speech = "I'm sorry, I did not understand your statement. " \
                 "Please enter your question or type 'options' for a list of options."

    return returnStatement(speech)

#first response after filter - if you typed historical or predictive
def getFilterAnswerWebhook(req):
    result = req.get("result")
    parameters = result.get("parameters")
    kpi = parameters.get("kpi")
    timeframe = parameters.get("timeframe")
    subject = parameters.get("subject")
    kpitype = parameters.get("kpi-type")
    kpiTimeFilter = parameters.get("kpi-time-filter")
    options = parameters.get("other-options")
    if kpi and timeframe and subject and kpitype:
        speech = "Awesome! I have all the information I need. " + checkForError(kpi, kpitype, timeframe, subject)
    elif kpiTimeFilter == "historical":
        speech = "How far back would you like to see results from?"
    elif kpiTimeFilter == "predictive":
        speech = "How far forward would you like to see results for?"
    elif options:
        speech = "Please select between 'historical' and 'predictive'."
    else:
        speech = "Please enter a valid timeframe."

    return returnStatement(speech)

#takes the timeframe you want and asks for the subject (customer, segment, etc.)
def getTimeFilterAnswerWebhook(req):
    historicalTimeframe = ['past month', 'past week', 'today', 'past year', 'beginning of time']
    result = req.get("result")
    parameters = result.get("parameters")
    timeframe = parameters.get("timeframe")
    kpiTimeFilter = parameters.get("kpi-time-filter")
    options = parameters.get("other-options")
    historicalTimeframe = ['past month', 'past week', 'today', 'past year', 'beginning of time']
    predictiveTimeframe = ['one month', 'three months', 'six months']
    if options:
        if kpiTimeFilter == "historical":
            speech = "Your options are '" + ("', '".join(str(x) for x in historicalTimeframe))+ "'"
        else:
            speech = "Your options are '" + ("', '".join(str(x) for x in predictiveTimeframe))+ "'"
    elif timeframe and (kpiTimeFilter == "historical" and timeframe in historicalTimeframe) or \
            (kpiTimeFilter == "predictive" and timeframe not in historicalTimeframe):
        speech = "Excellent! For which subject would you like to see these results?"
    else:
        speech = "This timeframe is not valid for " + kpiTimeFilter + " data. Please enter a valid timeframe."
        parameters["timeframe"] = ""

    return returnStatement(speech)


#takes the timeframe and subject and kpi information and determines whether to ask for average/sum or call checkforError
def getKpiFilterAnswer(req):
    result = req.get("result")
    parameters = result.get("parameters")
    timeframe = parameters.get("timeframe")
    kpi = parameters.get("kpi")
    subject = parameters.get("subject")
    options = parameters.get("other-options")
    #kpi that have average or sum values
    enterpriseKPI2 = ['acquisition cost', 'current value', 'retention cost', 'product processing cost',
                      'non-interest revenue', 'interest revenue',
                      'future value', 'customer lifetime value', 'referral/word of mouth value']
    #kpi that do not have average or sum values
    enterpriseKPI = ['purchase frequency', 'period since last purchase', 'product servicing fee',
                     'churn rate', 'lifetime duration']
    #products can only access these kpi
    productKPI = ['product processing cost', 'purchase frequency', 'non-interest revenue',
                  'product servicing fee', 'churn rate']
    kpiTimeFilter = parameters.get("kpi-time-filter")
    seHistoricalKPI = ['acquisition cost', 'current value', 'retention cost', 'product processing cost',
                      'non-interest revenue', 'interest revenue','purchase frequency',
                       'period since last purchase', 'product servicing fee']
    sePredictiveKPI= ['future value', 'customer lifetime value',
                      'referral/word of mouth value','churn rate', 'lifetime duration']
    historicalKPI = ['acquisition cost', 'current value', 'retention cost', 'product processing cost',
                     'purchase frequency',
                     'period since last purchase', 'non-interest revenue', 'interest revenue', 'product servicing fee']
    predictiveKPI = ['future value', 'customer lifetime value', 'referral/word of mouth value',
                     'customers with the highest probability to churn',
                     'customers with the highest probability to upsell/cross-sell',
                     'customers with the highest referral/word of mouth value',
                     'customers with the longest predicted lifetime duration',
                     'churn rate', 'lifetime duration']
    if options:
        if subject == "enterprise" or subject == "segment":
            if kpiTimeFilter == "historical":
                speech = "Your options are '" + ("', '".join(str(x) for x in seHistoricalKPI))+ "'"
            else:
                speech = "Your options are " + (", '".join(str(x) for x in sePredictiveKPI))+ "'"
        elif subject == "product":
            if kpiTimeFilter == "historical":
                speech = "Your options are '" + ("', '".join(str(x) for x in sePredictiveKPI if x != "churn rate"))+ "'"
            else:
                speech = "Your only option is 'churn rate'."
        elif subject == "customer":
            if kpiTimeFilter == "historical":
                speech = "Your options are '" + ("', '".join(str(x) for x in historicalKPI)) + "'"
            else:
                speech = "Your options are '" + ("', '".join(str(x) for x in predictiveKPI)) + "'"
    elif subject == "enterprise" or subject == "segment":
        if kpi in enterpriseKPI2:
            speech = "Would you like to see the average or sum value for this data?"
        elif kpi in enterpriseKPI:
            kpitype = ""
            speech = "Awesome! I have all the information that I need. " + checkForError(kpi, kpitype, timeframe,
                                                                                         subject)
        else:
            speech = "The data is not supported for this subject. Please enter a different subject to view this data."
    elif subject == "product":
        if kpi in productKPI:
            kpitype = ""
            speech = "Awesome! I have all the information that I need. " + \
                     checkForError(kpi, kpitype, timeframe, subject)
        else:
            speech = "The data is not supported for this subject. Please enter a different subject to view this data."
    else:
        kpitype = ""
        speech = "Awesome! I have all the information that I need. " + checkForError(kpi, kpitype, timeframe, subject)

    return returnStatement(speech)

#gets the subject and asks for what KPI you would like to see
def getSubjectFilterAnswerWebhook(req):
    result = req.get("result")
    parameters = result.get("parameters")
    subject = parameters.get("subject")
    options = parameters.get("other-options")
    if options:
        speech = "Your options are 'customer', 'segment', 'enterprise', 'product. "
    elif subject:
        speech = "Awesome! What type of data are you interested in seeing?"
    else:
        speech = "I'm sorry, I did not understand your statement. " \
                 "Please reword, or type 'options' for a list of options."

    return returnStatement(speech)

#more required webhook code
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')
