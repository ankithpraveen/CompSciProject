from django.shortcuts import render
import csv
from BookTicket.models import Account
import os
import mysql.connector
import datetime
from django.http import HttpResponseRedirect
import random
import time

con=mysql.connector.connect(host="localhost", user="root", passwd="root",database="project")
curs=con.cursor()

# Create your views here.

x=[]
train=[]
pnrlist=[]
tno=''
fdate=''
pnr=0
datedict={'Jan':1,'Feb':2,'Mar':3,'Apr':4,'May':5,'Jun':6,'Jul':7,'Aug':8,'Sep':9,'Oct':10,'Nov':11,'Dec':12}
daydict={1:'MON',2:'TUE',3:'WED',4:'THU',5:'FRI',6:'SAT',7:'SUN'}
flag=True

def seehomepg(request):
    global x
    x=[]
    return render(request,'Home_Page.html',{'al':x})
def seehome(request):
    global x
    return render(request,'Home_Page.html',{'al':x})
def seelogin(request):
    global x
    if request.method=="POST":
        email=request.POST['email']
        pwd=request.POST['password']
        print(email,pwd)
        curs.execute("select * from bookticket_account")
        acc=curs.fetchall()
        print(acc)
        for i in acc:
            print(i)
            # for j in i:
            if i[2]==email and i[3]==pwd:
                x=i
                print(x)
                return render(request,'Home_Page.html',{'al':i})
        else:
            return render(request,'Login.html')
    else:
        return render(request,'Login.html',{'al':[]})
        # email=request.POST['email']
        # pwd=request.POST['password']
        # a=Account.objects.all()
        # a_list=list(a)
        # for i in range(len(a_list)):
            # print(i)
            # if email==a_list[i].aemail and pwd==a_list[i].apwd:
                # x=a_list[i:i+1]
                # return render(request,'Home_Page.html',{'al':x})
            # else:
                # return render(request,'Login.html')
    # else:
    #     return render(request,'Login.html',{'al':[]})
def seepnr(request):
    global x
    if request.method=='POST':
        pnrno=request.POST['pnr']
        curs.execute("select passenger_name,pnr_no,train_no,seat_no,date,time,quota,status from bookticket_passenger p,bookticket_journey j where p.passenger_id=j.passenger_id and PNR_No={}".format(pnrno))
        pnrdetails=curs.fetchall()
        return render(request,'Tickets.html',{'al':x,'tickets':pnrdetails,'btest':False})
    else:    
        return render(request,'PNR status.html',{'al':x})
def seesearch(request):
    global train
    global x
    global datedict
    global fdate
    global flag
    if request.method=="POST":
        fromstat=request.POST['fromstat']
        tostat=request.POST['tostat']
        date=request.POST['date']
        datesplit=date.split('-')
        if len(datesplit)!=3:
            return render(request,'Search.html',{'al':x})
        year,month,dat=datesplit
        fdate=datetime.datetime(int(year),int(month),int(dat))
        day=fdate.isoweekday()
        print(fdate,'bye')
        # month=datedict[date[0:3]]
        # year=date[8:]
        # dat=date[4:6]
        # day=datetime.datetime(int(year),int(month),int(dat))
        # day1=day
        # day=day.isoweekday()
        curs.execute("select train_no,station_id from bookticket_stops where station_id in ('{}','{}')".format(fromstat,tostat))
        sid=curs.fetchall()
        stop=[]
        for i in range(len(sid)):
            for j in range(len(sid)):
                if j!=i and sid[i][0]==sid[j][0]:
                    if [sid[i],sid[j]][::-1] not in stop:
                        stop+=[[sid[i],sid[j]]]
        train=[]
        for t in stop:
            train_no=t[0][0]
            source=t[0][1]
            dest=t[1][1]
            curs.execute("select station_id,arrival_time from bookticket_stops where station_id in ('{}','{}')".format(source,dest))
            at=curs.fetchall()
            for i in at:
                if i[0]==source:
                    artime=i[1]
                if i[0]==dest:
                    deptime=i[1]
            curs.execute("select train_no,train_name from bookticket_train")
            tr=curs.fetchall()
            for i in tr:
                if i[0]==train_no:
                    train_name=i[1]
            curs.execute("select day from bookticket_stops where train_no={} and station_id='{}'".format(train_no,source))
            daycheck=curs.fetchall()
            for i in daycheck:
                if i[0]==daydict[day]:
                    train+=[(train_no,train_name,source,dest,artime,deptime)]
            if not train:
                return render(request,'Schedule.html',{'train':[],'al':x,'btest':True})    
            return HttpResponseRedirect('../schedule')
    else:
        return render(request,'Search.html',{'al':x})
def seereg(request):
    if request.method=="POST":
        name=request.POST['name']
        email=request.POST['email']
        pwd=request.POST['password']
        # repwd=request.POST['repassword']
        age=request.POST['age']
        with open('data.csv','a') as file:
            wcs=csv.writer(file)
            wcs.writerow(["name",name])
            wcs.writerow(["email",email])
            wcs.writerow(["pwd",pwd])
            # wcs.writerow(["repwd",repwd])
            wcs.writerow(["age",age])
        lst=Account()
        lst.aname=name
        lst.aemail=email
        lst.apwd=pwd
        lst.aage=age
        lst.save()
        a_list=Account.objects.all()
        a_list=list(a_list)
        print(a_list)    
        k=a_list[-1:]
        print(k)
        return render(request,'Home_Page.html',{'al':k}) 
    else:
        return render(request,'Register.html')
def seeschedule(request):
    global x
    global train
    global tno
    global pnrlist
    global pnr
    global flag
    tno=''
    if request.method=="POST":
        if x:
            for i in request.POST:
                if request.POST[i]=='Book':
                    tno=i
            pnr=random.randint(1000000000,9999999999)
            while True:
                if pnr not in pnrlist:
                    pnrlist+=[pnr]
                    break
            else:
                pnr=str(random.randint(1000000000,9999999999))
            return HttpResponseRedirect('../form')
        else:
            return HttpResponseRedirect('../login')
    else:
        if not flag:
            curs.execute('Select * from bookticket_train')
            trainall=curs.fetchall()
            return render(request,'Schedule.html',{'train':trainall,'al':x})
        else:
            t=train
            return render(request,'Schedule.html',{'train':t,'al':x,'btest':True})
def seeform(request):
    global x
    global train
    global pnrlist
    global tno
    global fdate
    global pnr
    if request.method=="POST":
        psgname=request.POST['name']
        age=request.POST['age']
        gender=request.POST['gender']
        quota=request.POST['quota']
        for i in train:
            if i[0]==tno:
                trtup=i
        tno=''
        seat=random.randint(1,50)
        date=fdate
        fdate=''
        user=x[1]
        print(date,'hi')
        curs.execute("insert into bookticket_passenger (Passenger_name,Gender,Age) values ('{}','{}',{})".format(psgname,gender,age))
        curs.execute("select passenger_id from bookticket_passenger")
        pid=curs.fetchall()[-1][0]
        print(pid)
        curs.execute("insert into bookticket_journey (PNR_No,Train_No,Seat_No,Date,Time,Booked_user,Passenger_id,Quota,Status)values('{}','{}',{},'{}','{}','{}',{},'{}','Booked')".format(pnr,trtup[0],seat,date,trtup[4],user,pid,quota))
        con.commit()
        time.sleep(3)
        return render(request,'Home_Page.html',{'al':x})
    else:
        return render(request,"Passenger Details.html",{'al':x,'pnr':pnr})
def seeticket(request):
    global x
    
    if request.method=="POST":
        print(request.POST)
        for i in request.POST:
            if request.POST[i]=='Cancel':
                curs.execute("update bookticket_journey set status='Cancelled' where pnr_no={}".format(i))
                con.commit()
                curs.execute("select passenger_name,pnr_no,train_no,seat_no,date,time,quota from bookticket_passenger p,bookticket_journey j where p.passenger_id=j.passenger_id and booked_user='{}' and status='Booked'".format(x[1]))
                tickbook=curs.fetchall()
                curs.execute("select passenger_name,pnr_no,train_no,seat_no,date,time,quota from bookticket_passenger p,bookticket_journey j where p.passenger_id=j.passenger_id and booked_user='{}' and status='Cancelled'".format(x[1]))
                tickcancel=curs.fetchall()
                time.sleep(2)
        return render(request,'Tickets.html',{'al':x,'tickets':tickbook,'cancel':tickcancel,'btest':True})
        
    else:
        if x:
            curs.execute("select passenger_name,pnr_no,train_no,seat_no,date,time,quota from bookticket_passenger p,bookticket_journey j where p.passenger_id=j.passenger_id and booked_user='{}' and status='Booked'".format(x[1]))
            tickbook=curs.fetchall()
            curs.execute("select passenger_name,pnr_no,train_no,seat_no,date,time,quota from bookticket_passenger p,bookticket_journey j where p.passenger_id=j.passenger_id and booked_user='{}' and status='Cancelled'".format(x[1]))
            tickcancel=curs.fetchall()
            return render(request,'Tickets.html',{'al':x,'tickets':tickbook,'cancel':tickcancel,'btest':True})
        else:
            return HttpResponseRedirect('../login')
