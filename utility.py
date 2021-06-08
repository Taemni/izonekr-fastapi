import re

def error(msg):
    return {'result':False, 'message':msg}

def remove_tag(content):
    cleanr =re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', content)
    return cleantext

def myNick(subject, myNick='위즈원'):
    subject = subject.replace('&lt;위즈원&gt;', myNick).replace('<위즈원>', myNick)
    subject = subject.replace(f'{myNick}가', f'{myNick}이')
    subject = subject.replace(f'{myNick}는', f'{myNick}은')
    subject = subject.replace(f'{myNick}를', f'{myNick}을')
    return subject