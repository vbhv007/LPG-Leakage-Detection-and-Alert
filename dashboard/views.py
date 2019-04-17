from django.shortcuts import render
from django.http import HttpResponse
import requests as req
import sqlite3
import smtplib
import time
import boto3

# Create your views here.

lpg = 0
co = 0
smoke = 0


def create_table():
    conn = sqlite3.connect('tarp.db')
    c = conn.cursor()
    c.execute(
        'CREATE TABLE IF NOT EXISTS history(id REAL, lpg REAL, co REAL, smoke REAL, dateStamp TEXT)')
    conn.commit()
    c.close()
    conn.close()


def data_entry(dataId, lpg, co, smoke, dateStamp):
    conn = sqlite3.connect('tarp.db')
    c = conn.cursor()
    largestId = read_id()
    if(largestId == None or largestId[0] != dataId):
        c.execute('INSERT INTO history(id, lpg, co, smoke, dateStamp) VALUES(?, ?, ?, ?, ?)',
                  (dataId, lpg, co, smoke, dateStamp))
    conn.commit()
    c.close()
    conn.close()


def read_id():
    conn = sqlite3.connect('tarp.db')
    c = conn.cursor()
    c.execute('SELECT id FROM history WHERE id = (SELECT MAX(id) FROM history)')
    data = c.fetchone()
    c.close()
    conn.close()
    return data


def read_data():
    conn = sqlite3.connect('tarp.db')
    c = conn.cursor()
    c.execute('SELECT * FROM history')
    data = c.fetchall()
    c.close()
    conn.close()
    return data


def index(request):
    # create_table()
    data = get_live_data()
    dicData = {
        'data': ['LPG: '+str(data['lpg'])+'ppm', 'CO: '+str(data['co'])+'ppm', 'Smoke: '+str(data['smoke'])+'ppm']
    }
    largestId = read_id()
    if(largestId == None or data['dataId'] != largestId[0]):
        data_entry(data['dataId'], data['lpg'], data['co'],
                   data['smoke'], data['dateStamp'])
        if (data['lpg'] >= 100 and data['co'] >= 100 and data['smoke'] >= 100):
            send_email(data['lpg'], data['co'], data['smoke'],
                       'enter email to send mail to')
            send_sms('enter phone number to send sms to',
                     data['lpg'], data['co'], data['smoke'])
    return render(request, 'dashboard/index.html', dicData)


def get_live_data():
    lpgUrl = 'https://api.thingspeak.com/channels/748890/fields/1.json'
    coUrl = 'https://api.thingspeak.com/channels/748891/fields/1.json'
    smokeUrl = 'https://api.thingspeak.com/channels/748892/fields/1.json'

    r = req.get(lpgUrl)
    if (r.status_code == 200):
        data = r.json()
        lpg = data['feeds'][-1]['field1']
    r = req.get(coUrl)
    if (r.status_code == 200):
        data = r.json()
        co = data['feeds'][-1]['field1']
    r = req.get(smokeUrl)
    if (r.status_code == 200):
        data = r.json()
        dataId = data['feeds'][-1]['entry_id']
        smoke = data['feeds'][-1]['field1']
        dateStamp = data['feeds'][-1]['created_at']
        data = {'dataId': dataId, 'lpg': lpg, 'co': co,
                'smoke': smoke, 'dateStamp': dateStamp}
    return data


def history(request):
    data = read_data()
    miniData = []
    for i in data:
        miniData.append([str(i[0]), str(i[1]), str(i[2]),
                         str(i[3]), str(i[4][:10]), i[4][11:-1]])
    dicData = {'data': miniData}
    return render(request, 'dashboard/history.html', dicData)


def helpline(request):
    return render(request, 'dashboard/helpline.html')


def send_email(lpg, co, smoke, recieverEmail):
    s = smtplib.SMTP()
    s.connect('email-smtp.us-east-1.amazonaws.com', 587)
    s.starttls()
    s.login('secret',
            'another secret')
    msg = "From: enter-sender-email\nTo: " + recieverEmail + "\nSubject: LPG Leakage Alert!\n\nAlert! Alert!\nThis is an auto-generated email sent from LPG Leakage Detection System. The value of LPG is " + \
        str(lpg) + "ppm and CO is " + str(co) + "ppm and Smoke is " + str(smoke) + \
        "ppm which are above normal values. Check the mobile app for more details.\nCall 101 for Fire emergency."
    s.sendmail('iamluciferms@gmail.com', recieverEmail, msg)


def send_sms(pNo, lpg, co, smoke):
    client = boto3.client('sns', 'us-east-1')
    msg = "Alert! Alert!\nThis is an auto-generated SMS sent from LPG Leakage Detection System. The value of LPG is " + \
        str(lpg) + "ppm and CO is " + str(co) + "ppm and Smoke is " + str(smoke) + \
        "ppm which are above normal values. Check the mobile app for more details.\nCall 101 for Fire emergency."
    client.publish(PhoneNumber=pNo, Message=msg)
