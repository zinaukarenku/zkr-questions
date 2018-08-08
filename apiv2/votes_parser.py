import bs4, json, os, time
#from selenium import webdriver  
#from selenium.webdriver.common.keys import Keys  
#from selenium.webdriver.chrome.options import Options
from selenium.common import exceptions as selexceptions
from urllib.parse import urlparse, parse_qs

from django.db import IntegrityError

from darbai.models import Link, Vote
from nariai.models import Politician
from .parsers import reverse_name

#step 0.1 - initial setup
#chrome_options = Options()
#chrome_options.add_argument("--headless")
#chrome_options.binary_location = '/usr/bin/chromium'

#driver = webdriver.Chrome(
#    executable_path=os.path.abspath("chromedriver"),
#    chrome_options=chrome_options
#)

#csss = driver.find_element_by_css_selector
#cssp = driver.find_elements_by_css_selector
#xpath = driver.find_element_by_xpath

#get the vote pages we will be parsing 

def read_given_vote(record, drv):
    #get the url of the voting page we'll actually be using
    urlp = urlparse(record.href)
    b_id = parse_qs(urlp[4])['p_bals_id'][0]
    drv.get('http://www.lrs.lt/sip/portal.show?p_r=15275&p_k=1&p_a=sale_bals&p_bals_id='+b_id)

    innerHTML = drv.find_element_by_css_selector('.tbl-default > tbody').get_attribute('innerHTML')
    soup = bs4.BeautifulSoup(innerHTML, 'lxml')

    for tr in soup.find_all('tr')[1:]:
        #skaitome balsą
        urlp = urlparse(tr.td.a.attrs['href'])
        asm_id = parse_qs(urlp[4])['p_asm_id'][0]
        name_lf = tr.td.a.text
        fraction = tr.find_all('td')[1].text

        if tr.find_all('td')[2]:
            vote = 'u'
        elif tr.find_all('td')[3]:
            vote = 'p'
        elif tr.find_all('td')[4]:
            vote = 's'
        else:
            vote = 'n'

        #duombazės operacijos
        #pirma, politikas:
        defaults = dict(name=reverse_name(name_lf))
        pol, created = Politician.objects.get_or_create(asm_id=asm_id, defaults=defaults)
        try:
            vote = Vote.objects.create(voter=pol,parent=record,vote=vote,fraction=fraction)
        except IntegrityError:
            continue

    try:
        decision = drv.find_element_by_xpath('/html/body/div[2]/div/div[7]/div/div[3]/b[10]').text
    except selexceptions.NoSuchElementException:
        pass
    else:
        if decision == "pritarta":
            record.balsavimas_result = 'p'
        elif decision == "atmesta":
            record.balsavimas_result = 'a'

    record.scanned = True
    record.save()

#driver.close()
