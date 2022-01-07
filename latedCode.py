# -*- coding: utf-8 -*-
"""
Created on Thu Dec  9 11:00:11 2021

@author: PremsaiGH
"""

from flask import Flask,jsonify,Response,request
from datetime import datetime
import requests
from flask_cors import CORS
import pyodbc
import simplejson as json


    

app = Flask(__name__)
CORS(app)
connStr = """DRIVER={SQL Server}; SERVER=CLM-MSL; Database=Crypto_App; UID=cnb_app_usr; PWD=Clarium@2021;"""

@app.route('/')
def index():
    return '<h1>Welcome to api world!</h1>'

@app.route('/api')
def api():
    url='https://x.wazirx.com/api/v2/tickers' 
    response=requests.get(url)
    
    #url = 'https://rest.coinapi.io/v1/assets'

    #headers = {'X-CoinAPI-Key' : '2E70B771-B951-4A85-BAA7-EFFC5E739A96'}

    #response = requests.get(url, headers=headers)
    r = Response(response=response ,status=200,mimetype="application/json")
    r.headers["Content-Type"] = "application/json; charset = utf-8"
    #r.headers["Content-length"] = "1000"
    return r

@app.route('/demo')
def demo():
    url='https://x.wazirx.com/api/v2/tickers' 
    response = requests.get(url)
    data = response.json()
    print(response)
    for v in data:
        c =  v
    print (c)
    #r = Response(response=c ,status=200,mimetype="application/json")
    #r.headers["Content-Type"] = "application/json; charset = utf-8"
    #r.headers["Content-length"] = "1000"
    #return r
    #response=requests.get(url)
    #for (k,v) in response.text:
     #   c = str(v)
    #p = Response(response=c,status=200,mimetype="application/json")
    #p.headers["Content-Type"] = "application/json; charset = utf-8"
    #return p 
    
@app.route('/transactiongetapi',methods=['GET'])
def transactiongetapi():
    conn = pyodbc.connect("""DRIVER={SQL Server}; SERVER=CLM-MSL; Database=Crypto_App; UID=cnb_app_usr; PWD=Clarium@2021;""")
    cursor = conn.cursor() 
    results=[]
    cursor.execute("""select * from dbo.User_Transaction""")
    columns = [column[0] for column in cursor.description]
    
    for row in cursor.fetchall():
        results.append(dict(zip(columns, row)))
    
    response = json.dumps(results, default=str)
    r = Response(response=response ,status=200,mimetype="application/json")
    r.headers["Content-Type"] = "application/json; charset = utf-8"
    #r.headers["Content-length"] = "1000"
    return r

@app.route('/transactiongetapibyid/<id>',methods=['GET'])
def transactiongetapibyid(id):
    conn = pyodbc.connect("""DRIVER={SQL Server}; SERVER=CLM-MSL; Database=Crypto_App; UID=cnb_app_usr; PWD=Clarium@2021;""")
    cursor = conn.cursor()
    results=[]
    query = "select * from dbo.User_Transaction where Login_Id='{}'".format(id)
    cursor.execute(query)
    columns = [column[0] for column in cursor.description]

    for row in cursor.fetchall():
        results.append(dict(zip(columns, row)))
    response = json.dumps(results, default=str)
    r = Response(response=response ,status=200,mimetype="application/json")
    r.headers["Content-Type"] = "application/json; charset = utf-8"
    #r.headers["Content-length"] = "1000"
    return r

@app.route('/transactionbuysellapi/<id>',methods=['POST'])
def transactionbuysellapi(id):
    ReqJson = request.json
    Coin_Name = ReqJson['Coin_Name']
    Coin_Price = ReqJson['Coin_Price']
    Total_number_of_coins = ReqJson['Total_number_of_coins']
    Total_Amount =ReqJson['Total_Amount']
    Transaction_Type = ReqJson['Transaction_Type']
    Exchange_point = ReqJson['Exchange_point']
    Date = datetime.now()
    conn = pyodbc.connect(connStr)
    cursor = conn.cursor()  
    query = """INSERT INTO dbo.User_Transaction([Coin_Name],[Coin_Price],[Total_number_of_coins],[Total_Amount],[Transaction_Type],[Exchange_point],[Transaction_timestamp],[Login_Id]) VALUES (?,?,?,?,?,?,?,?)"""
    args = (Coin_Name,Coin_Price,Total_number_of_coins,Total_Amount,Transaction_Type,Exchange_point,Date,id)
    cursor.execute(query,args)
    conn.commit()
    return "Coin bought successfully"
@app.route('/loginapi',methods=['GET','POST'])
def loginapi():
    if request.method == "POST":
        LogJson = request.json
        Email_Address = LogJson['Email_Address']
        Password_Field = LogJson['Password_Field']
        Phone_Number = LogJson['Phone_Number']
        conn = pyodbc.connect(connStr)
        cursor = conn.cursor()  
        query = """INSERT INTO dbo.User_Table([Email_Address],[Password_Field],[Phone_Number]) VALUES (?,?,?)"""
        args = (Email_Address,Password_Field,Phone_Number)
        cursor.execute(query,args)
        conn.commit()
        return "User added successfully"
    elif request.method == "GET":
        conn = pyodbc.connect("""DRIVER={SQL Server}; SERVER=CLM-MSL; Database=Crypto_App; UID=cnb_app_usr; PWD=Clarium@2021;""")
        cursor = conn.cursor() 
        results=[]
        cursor.execute("""select * from dbo.User_Table""")
        columns = [column[0] for column in cursor.description]
        
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))
    
    
        response = json.dumps(results, default=str)
        r = Response(response=response ,status=200,mimetype="application/json")
        r.headers["Content-Type"] = "application/json; charset = utf-8"
        #r.headers["Content-length"] = "1000"
        return r
@app.route('/profit/<id>',methods=['POST'])
def profit(id):
    ProfJson = request.json
    Exchange_point = ProfJson['Exchange_point']
    conn = pyodbc.connect(connStr)
    cursor = conn.cursor()
    query = """select ((select Total_Amount AS Selling_Price  from dbo.User_Transaction where Login_Id = ? AND Transaction_Type = 'Sell' AND Exchange_point = ?) - (select Total_Amount AS Cost_Price  from dbo.User_Transaction where Login_Id = ? AND Transaction_Type = 'Buy' AND Exchange_point = ?))*100/(select Total_Amount AS Cost_Price  from dbo.User_Transaction where Login_Id = ? AND Transaction_Type = 'Buy' AND Exchange_point = ?) AS Profit"""
    args = (id,Exchange_point,id,Exchange_point,id,Exchange_point)
    cursor.execute(query,args)
    results=[]
    columns = [column[0] for column in cursor.description]
    
    for row in cursor.fetchone():
        results.append(dict(zip(columns, row)))
    return jsonify(results)


@app.route('/ExchangeUsage/<id>', methods=['GET'])
def ExchangeUsage(id):
    conn = pyodbc.connect("""DRIVER={SQL Server}; SERVER=CLM-MSL; Database=Crypto_App; UID=cnb_app_usr; PWD=Clarium@2021;""")
    cursor = conn.cursor() 
    results=[]
    #query = "SELECT (SELECT SUM(Total_number_of_coins) from dbo.User_Transaction WHERE Login_Id=? and Exchange_Point='Bitrue.com' and Transaction_Type='Buy') AS BitrueBuy, (SELECT SUM(Total_number_of_coins) from dbo.User_Transaction WHERE Login_Id=? and Exchange_Point='Wazirx.com' and Transaction_Type='Buy') AS WazirxBuy, (SELECT SUM(Total_number_of_coins) from dbo.User_Transaction WHERE Login_Id=? and Exchange_Point='Crypto.com' and Transaction_Type='Buy') AS CryptoBuy"
    #val=(id,id,id)
    query = "SELECT Exchange_Point,sum(Total_number_of_coins) as total_cost from dbo.User_Transaction WHERE Login_Id=? group by Exchange_Point"
    val=(id)
    cursor.execute(query,val)
    columns = [column[0] for column in cursor.description]
    for row in cursor.fetchall():
        results.append(dict(zip(columns, row)))
    response = json.dumps(results, default=str) 
    r = Response(response=response ,status=200,mimetype="application/json")
    r.headers["Content-Type"] = "application/json; charset = utf-8"
    #r.headers["Content-length"] = "1000"
    return r
    

@app.route('/ProfitAndLossFromExchanges/<id>', methods=['GET'])
def ProfitAndLossFromExchanges(id):
    conn = pyodbc.connect("""DRIVER={SQL Server}; SERVER=CLM-MSL; Database=Crypto_App; UID=cnb_app_usr; PWD=Clarium@2021;""")
    cursor = conn.cursor() 
    results=[]
    query = "SELECT Total_Buys.Exchange_Point,CASE WHEN ((total_sales-total_cost)/total_sales)*100 > 0 THEN ((total_sales-total_cost)/total_sales)*100 ELSE 0 END as Profit,CASE WHEN ((total_sales-total_cost)/total_cost)*100  < 0 THEN ABS(((total_sales-total_cost)/total_cost)*100) ELSE 0 END as Loss FROM (select Exchange_Point,sum(Total_number_of_coins*Coin_Price) as total_cost from dbo.User_Transaction WHERE Transaction_Type='Buy' and Login_Id=? group by Exchange_Point) AS Total_Buys, (select Exchange_Point,sum(Total_number_of_coins*Coin_Price) as total_sales from dbo.User_Transaction WHERE Transaction_Type='Sell' and Login_Id=? group by Exchange_Point) AS Total_Sells WHERE Total_Buys.Exchange_Point = Total_Sells.Exchange_Point;"
    val=(id,id)
    cursor.execute(query,val)
    columns = [column[0] for column in cursor.description]
    
    for row in cursor.fetchall():
        results.append(dict(zip(columns, row)))
    response = json.dumps(results, default=str) 
    r = Response(response=response ,status=200,mimetype="application/json")
    r.headers["Content-Type"] = "application/json; charset = utf-8"
    #r.headers["Content-length"] = "1000"
    return r
    
'''
@app.route('/signUp', methods=['POST'])
def signUp():
    jsonUserData = request.get_json()
    conn = pyodbc.connect("""DRIVER={SQL Server}; SERVER=CLM-MSL; Database=Crypto_App; UID=cnb_app_usr; PWD=Clarium@2021;""")
    cursor = conn.cursor()
    query = """INSERT INTO dbo.User_Table([Email_Address],[Password_Field],[Phone_Number],[User_Name]) VALUES (?,?,?,?)"""
    #args = (Email_Address, Password_Field, Phone_Number,User_Name)
    args = (jsonUserData["Email_Address"],jsonUserData["Password_Field"],jsonUserData["Phone_Number"],jsonUserData["User_Name"]) 
    cursor.execute(query, args)
    conn.commit()
    return "Sucessfully added user"
'''


'''
@app.route('/login', methods=['POST'])
def login():
    jsonUserData = request.get_json()
    conn = pyodbc.connect("""DRIVER={SQL Server}; SERVER=CLM-MSL; Database=Crypto_App; UID=cnb_app_usr; PWD=Clarium@2021;""")
    cursor = conn.cursor()
    query ="""SELECT * FROM dbo.User_Table WHERE User_Name = ? and Password_Field = ?"""
    #vals = (Username,Password)
    vals = (jsonUserData["User_Name"],jsonUserData["Password_Field"])
    cursor.execute(query, vals)
    listrows=cursor.fetchone()
    if listrows==None:
        return jsonify(result=False)
    else:
        return jsonify(result=True)
    
    '''
    
@app.route('/login', methods=['POST'])
def login():
    jsonUserData = request.get_json()    
    conn = pyodbc.connect("""DRIVER={SQL Server}; SERVER=CLM-MSL; Database=Crypto_App; UID=cnb_app_usr; PWD=Clarium@2021;""")
    cursor = conn.cursor()
    query ="""SELECT * FROM dbo.User_Table WHERE User_Name = ? and Password_Field = ?"""
    #vals = (Username,Password)
    vals = (jsonUserData["User_Name"],jsonUserData["Password_Field"])
    cursor.execute(query, vals)
    logtrue={"result":"true"}
    listrows=cursor.fetchone()
    if listrows==None:
        return jsonify(result=False)
    else:
        results=[]
        columns = [column[0] for column in cursor.description]
    
    results.append(dict(zip(columns, listrows)))
    results.append(dict(logtrue))
    return jsonify(results)  

    
@app.route('/signUp', methods=['GET','POST'])
def signUp():
    jsonUserData = request.get_json()
    Email_Address = request.args.get('Email_Address')
    Password_Field = request.args.get('Password_Field')
    Phone_Number = request.args.get('Phone_Number')
    Username=request.args.get('User_Name')
    conn = pyodbc.connect("""DRIVER={SQL Server}; SERVER=CLM-MSL; Database=Crypto_App; UID=cnb_app_usr; PWD=Clarium@2021;""")
    cursor = conn.cursor()
    query2 = "select * from dbo.User_Table where Email_Address=? or User_Name=? "
    vals = (jsonUserData["Email_Address"],jsonUserData["User_Name"])
    cursor.execute(query2,vals)
    listrows=cursor.fetchone()
    signuptrue={"result":"True"}
    if listrows==None:
        query = """INSERT INTO User_Table(Email_Address,Password_Field,Phone_Number,User_Name) SELECT  ?, ?,? , ? WHERE NOT EXISTS (SELECT * FROM User_Table WHERE Email_Address = ? and User_Name=?)"""

        args = (jsonUserData["Email_Address"],jsonUserData["Password_Field"],jsonUserData["Phone_Number"],jsonUserData["User_Name"],jsonUserData["Email_Address"],jsonUserData["User_Name"])
        cursor.execute(query, args)
        conn.commit()
        query3 = "select * from dbo.User_Table where Email_Address=? and User_Name=? "
        vals = (jsonUserData["Email_Address"],jsonUserData["User_Name"])
        cursor.execute(query3,vals)
        
        results=[]
        columns = [column[0] for column in cursor.description]
        
             
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))
        results.append(dict(signuptrue))
        response = json.dumps(results, default=str) 
        r = Response(response=response ,status=200,mimetype="application/json")
        r.headers["Content-Type"] = "application/json; charset = utf-8"
        #r.headers["Content-length"] = "1000"
        return r
        
    else:
        
        return jsonify(result=False)
    
    

    
           
    
if __name__ == '__main__':
    app.run(debug=True)