import smtplib 
from email.mime.text import MIMEText

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
    
#mail
def send_image_failer(img_url):
    msg = MIMEText('ERROR: attepmted: ' + img_url)
    msg['Subject'] = 'MtgIntelligence Image Error'
    msg['From']    = 'crawler@mtgintelligence.com'
    msg['To']      = 'billysafina@yahoo.co.jp'

    s = smtplib.SMTP() 
    s.connect()
    s.sendmail(msg['From'], ['billysafina@yahoo.co.jp'], msg.as_string() )
    s.close()
    
#mail for log?
def send_mail(name):
    msg = MIMEText('Attepmted: ' + name)
    msg['Subject'] = 'MtgIntelligence Image Error'
    msg['From']    = 'crawler@mtgintelligence.com'
    msg['To']      = 'billysafina@yahoo.co.jp'

    s = smtplib.SMTP() 
    s.connect()
    s.sendmail(msg['From'], ['billysafina@yahoo.co.jp'], msg.as_string() )
    s.close()