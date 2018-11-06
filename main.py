#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2, re
import os, jinja2
import json
# import requests
import time
from google.appengine.api import urlfetch

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'template')
JINJA2_ENV = jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATE_DIR),
                               autoescape=True)

def render_str(template, **params):
    t = JINJA2_ENV.get_template(template)
    return t.render(params)
def validate_min_alpha_count(char):
    if len(char) < 3:
        return False
def validate_alphabet(alpha):
    ALP_RE = re.compile(r"^([a-zA-z]+$)")
    return alpha and ALP_RE.match(alpha)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        """
        Saves the programmer to write response.out.write
        everytime
        """
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        """
        Calls the global render_str()
        """
        return render_str(template, **params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class MainHandler(Handler):
    def __init__(self,request,response):
        self.initialize(request,response)
        self.tickerq = ""
        self.cname = ""
        self.ltime=""
        self.lprice = 0.0
        self.change = 0.0
        self.cpercent = 0.0
 
    def get(self):
        self.render("stock_info.html")

    def post(self):
        print 'inside post'
        have_error = False
        params = {}
        output ={}
        change_sign=''
        cpercent=0.0


        ticketSymbol = self.request.get('ticketSymbol') # Minimum 3
        #Check if blank
        if not validate_alphabet(ticketSymbol):
            have_error = True
            params['TKTSYM_ERROR'] = "Ticker accepts only letters."

        if len(ticketSymbol) < 3:
                have_error = True
                params['TKTSYM_ERROR'] = 'Ticker must have atleast 3 letters'

        params['ticketSymbol'] = ticketSymbol
        print 'ticketSymbol '+ticketSymbol
        domain = 'https://api.iextrading.com/1.0/stock/'
        final_url = domain + ticketSymbol + '/quote'
        print 'url '+final_url
        
        try:
            output = urlfetch.fetch(final_url)
            output = json.loads(output.content)
            print output
            if output:
                ltime = time.asctime( time.localtime(time.time()) )
                print ltime
                cname = output['companyName']
                print "Company Name: " + cname
                lprice = output['latestPrice']
                print "Latest Price: " + str(lprice)
                change = output['change']
                change_sign = "+"
                if(output['previousClose']>output['close']):
                    change_sign ='-'
                print 'Change: '+ change_sign+' '+str(change)
                cpercent = output['changePercent']
                print 'Change Percent(%): ' +change_sign+' '+ str(cpercent) + '%'
            # if result.status_code == 200:
            #     self.response.write(result.content)
            # else:
            #     self.response.status_code = result.status_code
        except:
            print 'I am in except'
            have_error = True
            print 'Please enter a valid symbol'
            params['TKTSYM_ERROR'] = 'Please enter a valid symbol'
            
        if have_error:
            self.render('stock_info.html',**params)
        else:
            self.tickerq = ticketSymbol.upper()
            self.ltime = ltime
            self.cname = cname
            self.lprice = lprice
            self.change = change
            self.cpercent = cpercent
            self.render('stockdata.html', ticker=self.tickerq, ltime=self.ltime, cname=self.cname, lprice=self.lprice,
            change=self.change,cpercent=self.cpercent)

class StockInfoHandler(MainHandler):
    def __init__(self,request,response):
        self.initialize(request,response)
        #MainHandler.__init__(self,request,response)

    def get(self):
        self.render('stockdata.html', ticker=self.tickerq,ltime=self.ltime,cname=self.cname, lprice=self.lprice,
        change=self.change,cpercent=self.cpercent)


app = webapp2.WSGIApplication([
    ('/', MainHandler),('/stockdata',StockInfoHandler)
], debug=True)
