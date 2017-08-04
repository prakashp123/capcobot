#!/usr/bin/env python

from __future__ import print_function

from future.standard_library import install_aliases

install_aliases()

import json
import os

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)


# required webhook code
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


# checks the request to see if it is valid - outputs nothing if no request action is found
def processRequest(req):
    context = req.get("result").get("contexts")
    if context == []:
        speech = "I'm sorry, I could not understand what you said. Please check your spelling, or " \
                 "type 'about' for more information."
        return returnStatement(speech)
    elif (req.get("result").get("action") != "list" and req.get("result").get("action") != "getWelcome" \
                  and req.get("result").get("action") != "welcomeAnswer" \
                  and req.get("result").get("action") != "getFilterAnswer" \
                  and req.get("result").get("action") != "getTimeFilterAnswer" \
                  and req.get("result").get("action") != "getKpiFilterAnswer" \
                  and req.get("result").get("action") != "welcomeAbout" \
                  and req.get("result").get("action") != "getSubjectFilterAnswer" \
                  and req.get("result").get("action") != "getPassword" \
                  and req.get("result").get("action") != "getHelp" \
                  and req.get("result").get("action") != "getValue" \
                  and req.get("result").get("action") != "getKPI" \
                  and req.get("result").get("action") != "getSubject" \
                  and req.get("result").get("action") != "getTimeframe" \
                  and req.get("result").get("action") != "getFaultyInput" \
                  and req.get("result").get("action") != "getCustomerID" \
                  and req.get("result").get("action") != "getSegmentName" \
                  and req.get("result").get("action") != "passwordWelcome"):
        speech = "I'm sorry, I could not understand what you said. Please check your spelling, or " \
                 "type 'about' for more information."
        return returnStatement(speech)

    if req.get("result").get("action") == "list":
        res = makeWebhookResult(req)
    elif req.get("result").get("action") == "passwordWelcome":
        res = getPasswordWebhook(req)
    elif req.get("result").get("action") == "getPassword":
        res = processPassword(req)
    elif req.get("result").get("action") == "getHelp":
        res = getHelp(req)
    elif req.get("result").get("action") == "getValue":
        res = getValue(req)
    elif req.get("result").get("action") == "getKPI":
        res = getKPI(req)
    elif req.get("result").get("action") == "getSubject":
        res = getSubject(req)
    elif req.get("result").get("action") == "getTimeframe":
        res = getTimeframe(req)
    elif req.get("result").get("action") == "welcomeAnswer":
        res = getWelcomeAnswerWebhook(req)
    elif req.get("result").get("action") == "welcomeAbout":
        res = welcomeAbout(req)
    elif req.get("result").get("action") == "getCustomerID":
        res = getCustomerID(req)
    elif req.get("result").get("action") == "getSegmentName":
        res = getSegmentName(req)
    elif req.get("result").get("action") == "getFilterAnswer":
        res = getFilterAnswerWebhook(req)
    elif req.get("result").get("action") == "getTimeFilterAnswer":
        res = getTimeFilterAnswerWebhook(req)
    elif req.get("result").get("action") == "getKpiFilterAnswer":
        res = getKpiFilterAnswer(req)
    elif req.get("result").get("action") == "getSubjectFilterAnswer":
        res = getSubjectFilterAnswerWebhook(req)
    else:
        res = getFaultyInput(req)

    return res


# main return statement
def returnStatement(speech):
    return {
        "speech": speech,
        "displayText": speech,
        "data": {},
        "contextOut": [],
        "source": "chatbot"
    }


# main welcome text - asks for password
def getPasswordWebhook(req):
    result = req.get("result")
    action = result.get("action")
    if action == "passwordWelcome":
        speech = "Please enter your password."
    else:
        speech = "Sorry, I couldn't understand your sentence."

    return returnStatement(speech)


# checks password to see if valid - if valid, grants access to the bot.
# api.ai giving an error here
def processPassword(req):
    result = req.get("result")
    parameters = result.get("parameters")
    password = parameters.get("password")
    if password == "123":
        return getWelcomeWebhook(req)

    else:
        speech = "This is an invalid password."
        return returnStatement(speech)


# WORKING CHATBOT CODE IS BELOW



# getWelcomeWebhook and getWelcomeAnswerWebhook greet the user and ask if he/she would like to filter for results or
# simply ask a question
# welcoming intent after password is authenticated
def getWelcomeWebhook(req):
    result = req.get("result")
    action = result.get("action")
    if action == "getPassword":
        speech = "Welcome to the CapcoBot. Type in your question in English, or type 'wizard' for more options."
    else:
        speech = "Sorry, I couldn't understand your sentence."

    return returnStatement(speech)


def welcomeAbout(req):
    result = req.get("result")
    parameters = result.get("parameters")
    about = parameters.get("about")
    if about:
        speech = "The Capcobot is a premium bot designed to give results rearding different " \
                 "characteristics about customers. To learn more about what type of data can be seen, type 'wizard'."

    return returnStatement(speech)


# determines whether you type 'filter' or your query
def getWelcomeAnswerWebhook(req):
    result = req.get("result")
    parameters = result.get("parameters")
    filter = parameters.get("filter")
    kpi = parameters.get("kpi")
    timeframe = parameters.get("timeframe")
    subject = parameters.get("subject")
    kpitype = parameters.get("kpi-type")
    '''customerID = parameters.get("customerID")
    segmentName = parameters.get("segmentName")
    productName = parameters.get("productName")
    yesno = parameters.get("yesno")'''
    if (filter and kpi and kpitype and subject and timeframe) or \
            (kpi and kpitype and subject and timeframe) or \
            (kpi and timeframe and (subject == "customer" or subject == "product")):
        speech = "hi"
        # speech = "Okay, here we go: " \
        #         + checkForError(kpi, kpitype, timeframe, subject, customerID, segmentName, productName)
    elif filter and not (kpi or kpitype or subject or timeframe):
        speech = "I will guide you through the process to get the answers to your questions.\n" \
                 " Are you interested in historical or predictive data?"
        # elif yesno:
        #   speech = "Are you interested in historical or predictive data?"
    else:
        speech = "I'm sorry, I did not understand your statement. " \
                 "Please enter your question or type 'options' for a list of options."

    return returnStatement(speech)


def filterAbout(req):
    result = req.get("result")
    parameters = result.get("parameters")
    about = parameters.get("about")
    if about:
        speech = "'Historical' refers to information regarding the past, up until today. 'Predictive' " \
                 "refers to the future, where we predict future results based on the information we have now."

    return returnStatement(speech)


# first response after filter - if you typed historical or predictive
def getFilterAnswerWebhook(req):
    result = req.get("result")
    parameters = result.get("parameters")
    kpi = parameters.get("kpi")
    timeframe = parameters.get("timeframe")
    subject = parameters.get("subject")
    kpitype = parameters.get("kpi-type")
    kpiTimeFilter = parameters.get("kpi-time-filter")
    options = parameters.get("other-options")
    '''customerID = parameters.get("customerID")
    segmentName = parameters.get("segmentName")
    productName = parameters.get("productName")'''
    if kpi and timeframe and subject and kpitype:
        speech = "hi"
        # speech = "I have all the information I need.\n " \
        #        + checkForError(kpi, kpitype, timeframe, subject, customerID, segmentName, productName)
    elif kpiTimeFilter == "historical":
        speech = "How far back would you like to see results from?" \
                 " If you do not know, type 'options' for a list of options"
    elif kpiTimeFilter == "predictive":
        speech = "How far forward would you like to see results for?"
    elif options:
        speech = "Please select between 'historical' and 'predictive'."
    else:
        speech = "Please enter a valid timeframe."

    return returnStatement(speech)


# takes the timeframe you want and asks for the subject (customer, segment, etc.)
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
            speech = "Your options are \n''" + ("' \n'".join(str(x) for x in historicalTimeframe)) + "'"
        else:
            speech = "Your options are '\n''" + ("' \n'".join(str(x) for x in predictiveTimeframe)) + "'"
    elif timeframe and (kpiTimeFilter == "historical" and timeframe in historicalTimeframe) or \
            (kpiTimeFilter == "predictive" and timeframe not in historicalTimeframe):
        speech = "Okay. Would you like to see results on a customer, segment enterprise or product level?" \
                 " If you do not know, type 'options for a list of options"
    else:
        speech = "This timeframe is not valid for " + kpiTimeFilter + " data. Please enter a valid timeframe."

    return returnStatement(speech)


# gets the subject and asks for what KPI you would like to see
def getSubjectFilterAnswerWebhook(req):
    result = req.get("result")
    parameters = result.get("parameters")
    subject = parameters.get("subject")
    options = parameters.get("other-options")
    timeframe = parameters.get("timeframe")
    if options and timeframe:
        speech = "Your options are 'customer'\n 'segment'\n 'enterprise'\n 'product. "
    elif subject == "customer":
        speech = "Okay. What is the customer ID? The acceptable format is ID XXXXX"
    elif subject == "segment":
        speech = "Okay. What is the segment name?"
    elif subject == "enterprise":
        speech = "Okay. What KPI are you interested in seeing?" \
                 "If you do not know, type 'options for more options"
    elif subject == "product":
        speech = "Okay. What is the product name?"
    else:
        speech = "I'm sorry, I did not understand your statement. " \
                 "Please reword, or type 'options' for a list of options."

    return returnStatement(speech)



def getCustomerID(req):
    result = req.get("result")
    parameters = result.get("parameters")
    subject = parameters.get("subject")
    customerID = parameters.get("customerID")
    number = parameters.get("number")
    sNumber = int(number)
    if subject == "customer" and sNumber < 100000 and sNumber >-1:
        speech = "Okay. What KPI are you interested in seeing? " \
                 "If you do not know, type 'options for a list of options"
    else:
        speech = "This is not a valid customer ID. " \
                 "Please reword, or type 'options' for a list of options."

    return returnStatement(speech)

def getSegmentName(req):
    result = req.get("result")
    parameters = result.get("parameters")
    subject = parameters.get("subject")
    segmentName = parameters.get("segmentName")
    if subject == "segment" and segmentName:
        speech = "Okay. What KPI are you interested in seeing? " \
                 "If you do not know, type 'options for a list of options"
    else:
        speech = "I'm sorry, I did not understand your statement. " \
                 "Please reword, or type 'options' for a list of options."

    return returnStatement(speech)

'''
def getProductName(req):
    result = req.get("result")
    parameters = result.get("parameters")
    subject = parameters.get("subject")
    productName = parameters.get("productName")
    if subject == "product" and productName:
        speech = "Okay. What KPI are you interested in seeing? " \
                 "If you do not know, type 'options for a list of options"
    else:
        speech = "I'm sorry, I did not understand your statement. " \
                 "Please reword, or type 'options' for a list of options."

    return returnStatement(speech)
'''


# takes the timeframe and subject and kpi information and determines
# whether to ask for average/sum or call checkforError
def getKpiFilterAnswer(req):
    result = req.get("result")
    parameters = result.get("parameters")
    timeframe = parameters.get("timeframe")
    kpi = parameters.get("kpi")
    subject = parameters.get("subject")
    options = parameters.get("other-options")
    customerID = parameters.get("customerID")
    snumber = parameters.get("number")
    strnumber = int(snumber)
    segmentName = ""
    productName = ""
    # kpi that have average or sum values
    enterpriseKPI2 = ['acquisition cost', 'current value', 'retention cost', 'product processing cost',
                      'non-interest revenue', 'interest revenue',
                      'future value', 'customer lifetime value', 'referral/word of mouth value']
    # kpi that do not have average or sum values
    enterpriseKPI = ['purchase frequency', 'period since last purchase', 'product servicing fee',
                     'churn rate', 'lifetime duration']
    # products can only access these kpi
    productKPI = ['product processing cost', 'purchase frequency', 'non-interest revenue',
                  'product servicing fee', 'churn rate']
    kpiTimeFilter = parameters.get("kpi-time-filter")
    seHistoricalKPI = ['acquisition cost', 'current value', 'retention cost', 'product processing cost',
                       'non-interest revenue', 'interest revenue', 'purchase frequency',
                       'period since last purchase', 'product servicing fee']
    sePredictiveKPI = ['future value', 'customer lifetime value',
                       'referral/word of mouth value', 'churn rate', 'lifetime duration']
    historicalKPI = ['acquisition cost', 'current value', 'retention cost', 'product processing cost',
                     'purchase frequency',
                     'period since last purchase', 'non-interest revenue', 'interest revenue', 'product servicing fee']
    predictiveKPI = ['future value', 'customer lifetime value', 'referral/word of mouth value',
                     'customers with the highest probability to churn',
                     'customers with the highest probability to upsell/cross-sell',
                     'customers with the highest referral/word of mouth value',
                     'customers with the longest predicted lifetime duration',
                     'churn rate', 'lifetime duration']
    if kpi and timeframe and (subject == "customer" or subject == "product"):
        kpitype = ""
        speech = "Okay, here you go:\n " + checkForError(kpi, kpitype, timeframe, subject, customerID, strnumber,
                                                         segmentName,
                                                         productName)
    if options:
        if subject == "enterprise" or subject == "segment":
            if kpiTimeFilter == "historical":
                speech = "Your options are \n'" + ("' \n'".join(str(x) for x in seHistoricalKPI)) + "'"
            else:
                speech = "Your options are \n''" + ("' \n'".join(str(x) for x in sePredictiveKPI)) + "'"
        elif subject == "product":
            if kpiTimeFilter == "historical":
                speech = "Your options are \n'" + (
                    "' \n'".join(str(x) for x in sePredictiveKPI if x != "churn rate")) + "'"
            else:
                speech = "Your only option is 'churn rate'."
        elif subject == "customer":
            if kpiTimeFilter == "historical":
                speech = "Your options are \n'" + ("' \n'".join(str(x) for x in historicalKPI)) + "'"
            else:
                speech = "Your options are \n'" + ("' \n'".join(str(x) for x in predictiveKPI)) + "'"
    elif subject == "enterprise" or subject == "segment":
        if kpi in enterpriseKPI2:
            speech = "Would you like to see the average or sum value for this data?"
        elif kpi in enterpriseKPI:
            kpitype = ""
            speech = "Okay, here you go:\n " \
                    + checkForError(kpi, kpitype, timeframe, subject, customerID, segmentName, productName)
        else:
            speech = "The data is not supported for this subject. Please enter a different subject to view this data."
    elif subject == "product":
        if kpi in productKPI:
            kpitype = ""
            speech = "Okay, here you go:\n " + \
                    checkForError(kpi, kpitype, timeframe, subject, customerID, segmentName, productName)
        else:
            speech = "The data is not supported for this subject. Please enter a different subject to view this data."
    else:
        kpitype = ""
        speech = "Okay, here you go:\n " + checkForError(kpi, kpitype, timeframe, subject, customerID, strnumber, segmentName,
                                                        productName)

    return returnStatement(speech)


# makeWebhookResult is called when all parameters are given at once
# calls checkForError to output the result
def makeWebhookResult(req):
    result = req.get("result")
    parameters = result.get("parameters")
    kpi = parameters.get("kpi")
    timeframe = parameters.get("timeframe")
    subject = parameters.get("subject")
    kpitype = parameters.get("kpi-type")
    typos = parameters.get("typos")
    '''customerID = parameters.get("customerID")
    segmentName = parameters.get("segmentName")
    productName = parameters.get("productName")'''
    if typos:
        speech = "You said the word 'value'. What kind of value? Type 'cv' for current value, 'fv' for future value, " \
                 "'rwmv' for referral/word of mouth value, or 'clv' for customer liftetime value"
        return returnStatement(speech)
    else:
        # speech = checkForError(kpi, kpitype, timeframe, subject, customerID, segmentName, productName)
        speech = "Hi"
        return returnStatement(speech)


# this the main output function
# takes in all significant parameters - this is where the actual results would be outputted
def checkForError(kpi, kpitype, timeframe, subject, customerID, number, segmentName, productName):
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
    if kpi:
        if kpi in historicalKPI:
            hkpi = True
        elif kpi in predictiveKPI:
            pkpi = True
        else:
            bkpi = True
    if timeframe:
        if timeframe in historicalTimeframe:
            ht = True
        else:
            pt = True
    if not subject:
        speech = "You did not mention a subject. What subject would you like to see this data for?"
    elif not kpi:
        speech = "You did not mention a KPI. What KPI would you like to see data for?"
    elif not timeframe:
        speech = "You did not mention a subject. What subject would you like to see this data for?"
    elif not (kpi or kpitype or timeframe or subject):
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
    elif not timeframe and ((kpi and subject) or (kpi and subject and kpitype)):
        speech = "For what time period would you like to see these results?"
    elif not subject and ((kpi and timeframe) or (kpi and kpitype and timeframe) or (kpi and kpitype)):
        speech = "Just a little more information. Which group are you interested in?"
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
        if subject == "customer":
            speech = speech = "Okay, here we go: \n" \
             "The " + kpi + " for " + subject + " " + customerID + " " + number + " for the " + timeframe + ": $100.00\n" \
                                                                                             "Would you like to see " \
                                                                                             "another KPI? "
        elif subject == "segment":
            speech = returnFormatSegment(subject, kpi, kpitype, timeframe, segmentName)
        elif subject == "enterprise":
            speech = returnFormatEnterprise(subject, kpi, kpitype, timeframe)
        elif subject == "product":
            speech = returnFormatProduct(subject, kpi, timeframe, productName)

    print("Response:")
    print(speech)

    return speech


def getHelp(req):
    result = req.get('result')
    parameters = result.get('parameters')
    help = parameters.get('help')
    if help:
        speech = "Type in your question in English, or type 'wizard' for a more directed approach."

    return returnStatement(speech)


def getFaultyInput(req):
    speech = "I didn't understand what you said. Check your spelling and try again."
    return returnStatement(speech)


def getValue(req):
    speech = "You said the word 'value'. What kind of value? Type 'cv' for current value, 'fv' for future value, " \
             "'rwmv' for referral/word of mouth value, or 'clv' for customer liftetime value"
    return returnStatement(speech)


def getSubject(req):
    speech = "I just need one last piece of information. What subject would you like to see this information for? " \
             "If you do not know, type 'options for a list of options"
    return returnStatement(speech)


def getKPI(req):
    speech = "I just need one last piece of information. What KPI would you like to see this information for? " \
             "If you do not know, type 'options for a list of options"
    return returnStatement(speech)


def getTimeframe(req):
    speech = "I just need one last piece of information. What timeframe would you like to see this information for? " \
             "If you do not know, type 'options for a list of options"
    return returnStatement(speech)


def returnFormatCustomer(subject, kpi, timeframe, customerID,number):
    speech = "Okay, here we go: \n" \
             "The " + kpi + " for " + subject + " " + customerID + " " + number + " for the " + timeframe + ": $100.00\n" \
                                                                                             "Would you like to see " \
                                                                                             "another KPI? "

    return speech


def returnFormatSegment(subject, kpi, kpitype, timeframe, segmentName):
    speech = "Okay, here we go: \n" \
             "The " + kpitype + " " + kpi + " for " + subject + " " + segmentName + \
             " for the " + timeframe + ": $100.00\n" \
                                       "Would you like to see another KPI? "

    return speech


def returnFormatEnterprise(subject, kpi, kpitype, timeframe):
    speech = "Okay, here we go: \n" \
             "The " + kpitype + " " + kpi + " for " + subject + " " + \
             " for the " + timeframe + ": $100.00\n" \
                                       "Would you like to see another KPI? "

    return speech


def returnFormatProduct(subject, kpi, timeframe, productName):
    speech = "Okay, here we go: \n" \
             "The " + " " + kpi + " for " + subject + " " + productName + \
             " for the " + timeframe + ": $100.00\n" \
                                       "Would you like to see another KPI? "

    return speech


# more required webhook code
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')
