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


def processRequest(req):
    if req.get("result").get("action") != "list" and req.get("result").get("action") != "getWelcome":
        return {}
    if req.get("result").get("action") == "list":
        res = makeWebhookResult(req)
    else:
        res = getWelcomeWebhook(req)

    return res


def makeWebhookResult(req):
    result = req.get("result")
    parameters = result.get("parameters")
    kpi = parameters.get("kpi")
    timeframe = parameters.get("timeframe")
    subject = parameters.get("subject")
    kpitype = parameters.get("kpi-type")
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

    speech = checkForError(kpi,kpitype,timeframe,subject,pt,ht,hkpi,pkpi,bkpi)
    return {
        "speech": speech,
        "displayText": speech,
        "data": {},
        "contextOut": [],
        "source": "chatbot"
    }

def checkForError(kpi,kpitype,timeframe,subject,pt,ht,hkpi,pkpi,bkpi):
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
                                    kpi != "product processing cost" or kpi != "purchase frequency" or kpi != "product servicing fee" or kpi != "non-interest revenue"):
        speech = "This is an invalid statement. Are you interested in products?"
    elif subject == "product" and pt and pkpi != "churn rate":
        speech = "This is an invalid statement. Are you interested in statistics about products?"
    elif (subject == "enterprise" or subject == "segment") and ht and bkpi and not hkpi:
        speech = "This is an invalid statement. Are you interested in statistics about " + subject + "?"
    elif (subject == "enterprise" or subject == "segment") and ht and ((kpi != "purchase frequency" or
                                                                                kpi != "period since last purchase" or kpi != "product servicing frequency")) and not kpitype:
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
            speech = "Here is the list for the " + kpitype + " " + kpi + " for each " + subject + " for the " + timeframe + ":"
        elif kpi == "most profitable customers" or kpi == "least profitable customers":
            speech = "Here is the list for the " + kpi + " for the " + timeframe
        else:
            speech = "Here is the list for the " + kpi + " for each " + subject + " for the " + timeframe + ":"

    print("Response:")
    print(speech)

    return speech

def getWelcomeWebhook(req):
    result = req.get("result")
    action = result.get("action")
    if action == "getWelcome":
        speech = "Hi! This is the CapcoBot. Please enter your question, or type 'filter' for more options."
    else:
        speech = "Sorry, I couldn't understand your sentence."

    return {
        "speech": speech,
        "displayText": speech,
        "data": {},
        "contextOut": [],
        "source": "chatbot"
    }

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')
