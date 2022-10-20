import smtplib 
import subprocess
import os
import re
import requests
from email.mime.text import MIMEText
from selenium.common.exceptions import NoSuchElementException
import hashlib
from datetime import datetime as dt

#要素が存在するかのチェック
def check_exists_by_xpath(driver, xpath):
    try:
        driver.find_element_by_xpath(xpath)
    except NoSuchElementException:
        return False
    return True

#mail
def send_error_mail(args):
    msg = MIMEText('ERROR: attepmted: ' + args)
    msg['Subject'] = 'MtgIntelligence Error'
    msg['From']    = 'crawler@mtgintelligence.com'
    msg['To']      = 'billysafina@yahoo.co.jp'

    s = smtplib.SMTP() 
    s.connect()
    s.sendmail(msg['From'], ['billysafina@yahoo.co.jp'], msg.as_string() )
    s.close()
    
#image obtain
def getImage(url, name, lang):
    res = requests.get(url, stream=True)
    if res.status_code == 200:
        tdatetime = dt.now()
        tstr = tdatetime.strftime('%Y%m%d%H%M%S%f')
        
        file_name = name.lower()
        file_name = re.sub(',', '_', file_name)
        file_name = re.sub(' // ', '_', file_name)
        file_name = re.sub(' ', '_', name) + '_' + lang + '_' + tstr
        
        file_name = hashlib.md5(file_name.encode('utf-8')).hexdigest() + '.png'
        
        with open(file_name, 'wb') as file:
            for chunk in res.iter_content(chunk_size=1048576):
                file.write(chunk)
                command = ['swift', 'upload', 'mtg_public', file_name, '-q', '-R', '3']
                subprocess.call(command)
                os.remove(file_name)
        
        return file_name