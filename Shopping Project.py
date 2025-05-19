import datetime
import sqlite3
import tkinter
import re
from datetime import date
import time
import json


def updateJsonFile():
    with open('locked_users.json') as f:
        datalst = json.load(f)
    lst1 = []
    for x in datalst:
        if datalst[x]["attempts"] < 3:
            lst1.append(x)
    for y in lst1:
        datalst.pop(y)
    with (open('locked_users.json', 'w') as f):
        json.dump(datalst, f)

def readJson():
    with open('app_design.json') as f:
        return json.load(f)


def fwrite(datalst, fname):
    with open(fname, 'w') as f:
        for x in datalst:
            f.write(x + " ")

def packlist(lst):
    for x in lst:
        x.pack()

def readsql(sql):
    result = cnt.execute(sql)
    return result.fetchall()

def log():
    colordict = readJson()["Login Info"]

    def info():
        winInfo = tkinter.Toplevel(win)
        winInfo.title('Login Info')
        winInfo.geometry('450x200')
        winInfo.configure(bg=colordict["bg color"])

        lstbox = tkinter.Listbox(winInfo, width=70)
        lstbox.pack(pady=5)
        with open('users.log') as f:
            txtlist = f.read().split("\n")
        for txt in txtlist:
            lstbox.insert('end', txt)

    btnLog = tkinter.Button(win, text="Login Info", command=info, width=18)
    btnLog.pack()

def adminPanel():
    colordict = readJson()["Admin Panel"]

    def admin():
        def productVal(n):
            sql = f'''
                    SELECT * FROM products WHERE pname="{n}"
                '''
            data = readsql(sql)
            if len(data) == 0:
                lblMSG5.configure(text="Product Does Not Exist!", fg=colordict["msg2 color"])
                return False
            return True

        def countVal(c):
            if not c.isdigit() or int(c) <= 0:
                lblMSG5.configure(text="Product Count Must Be a Positive Number!", fg=colordict["msg2 color"])
                return False
            return True

        def priceVal(p):
            try:
                p = float(p)
                if p < 0:
                    lblMSG5.configure(text="Product Price Must Be a Positive Number!", fg=colordict["msg2 color"])
                    return False
                return True
            except:
                lblMSG5.configure(text="Product Price Must Be a Positive Number!", fg=colordict["msg2 color"])
                return False

        def updateproducts(sql):
            cnt.execute(sql)
            cnt.commit()
            lblMSG5.configure(text="Products List Updated Successfully!", fg=colordict["msg1 color"])
            txtName.delete(0, 'end')
            txtCount.delete(0, 'end')
            txtPrice.delete(0, 'end')
            lstbox.delete(0, 'end')
            products = getAllProducts()
            for product in products:
                text = f'Id : {product[0]} , Name : {product[1]} , Number : {product[2]} , Price : {product[3]}'
                lstbox.insert('end', text)

        def add():
            try:
                n = txtName.get()
                c = txtCount.get()
                p = txtPrice.get()
                if not countVal(c):
                    return
                if not priceVal(p):
                    return
                sql = f'''
                        INSERT INTO products (pname, number, price)
                        VALUES ("{n}",{c},{p})
                    '''
                updateproducts(sql)
            except:
                lblMSG5.configure(text="Something Went Wrong while Connecting to the Database!", fg=colordict["msg2 color"])

        def delete():
            try:
                n = txtName.get()
                if not productVal(n):
                    return
                sql = f'''
                        DELETE FROM products WHERE pname="{n}"
                    '''
                updateproducts(sql)
            except:
                lblMSG5.configure(text="Something Went Wrong while Connecting to the Database!", fg=colordict["msg2 color"])

        def count():
            try:
                n = txtName.get()
                c = txtCount.get()
                if not productVal(n):
                    return
                if not countVal(c):
                    return
                sql = f'''
                    UPDATE products SET number={c} WHERE pname="{n}"
                '''
                updateproducts(sql)
            except:
                lblMSG5.configure(text="Something Went Wrong while Connecting to the Database!", fg=colordict["msg2 color"])

        def price():
            try:
                n = txtName.get()
                p = txtPrice.get()
                if not productVal(n):
                    return
                if not priceVal(p):
                    return
                sql = f'''
                    UPDATE products SET price={p} WHERE pname="{n}"
                '''
                updateproducts(sql)
            except:
                lblMSG5.configure(text="Something Went Wrong while Connecting to the Database!", fg=colordict["msg2 color"])

        winAdmin = tkinter.Toplevel(win)
        winAdmin.title('Admin Panel')
        winAdmin.geometry('450x450')
        winAdmin.configure(bg=colordict["bg color"])

        lstbox = tkinter.Listbox(winAdmin, width=70)
        lstbox.pack(pady=5)
        products = getAllProducts()
        for product in products:
            text = f'Id : {product[0]} , Name : {product[1]} , Number : {product[2]} , Price : {product[3]}'
            lstbox.insert('end', text)

        lblName = tkinter.Label(winAdmin, text="Product Name: ", bg=colordict["bg color"])
        txtName = tkinter.Entry(winAdmin, width=30, bg=colordict["txtbox color"])
        lblCount = tkinter.Label(winAdmin, text="Product Count: ", bg=colordict["bg color"])
        txtCount = tkinter.Entry(winAdmin, width=30, bg=colordict["txtbox color"])
        lblPrice = tkinter.Label(winAdmin, text="Product Price: ", bg=colordict["bg color"])
        txtPrice = tkinter.Entry(winAdmin, width=30, bg=colordict["txtbox color"])

        lblMSG5 = tkinter.Label(winAdmin, text="", bg=colordict["bg color"])

        btnDelete = tkinter.Button(winAdmin, text="DELETE", width=20, command=delete)
        btnAdd = tkinter.Button(winAdmin, text="ADD", width=20, command=add)
        btnCount = tkinter.Button(winAdmin, text="CHANGE COUNT", width=20, command=count)
        btnPrice = tkinter.Button(winAdmin, text="CHANGE PRICE", width=20, command=price)

        lst = [lblName, txtName, lblCount, txtCount, lblPrice, txtPrice, lblMSG5, btnDelete, btnAdd, btnCount, btnPrice]
        packlist(lst)
        winAdmin.mainloop()

    btnAdmin = tkinter.Button(win, text="Admin Panel", command=admin, width=18)
    btnAdmin.pack()

def login():
    colordict = readJson()["Shop Project"]

    def isLoggedOut(username):
        with open('locked_users.json') as f:
            datalst = json.load(f)
        if username in datalst:
            if datalst[username]["attempts"] == 3:
                if time.time() - datalst[username]["last_attempt"] < (7*24*3600):
                    return True
                else:
                    datalst.pop(username)
                    with open('locked_users.json', 'w') as f:
                        json.dump(datalst, f)
        return False

    def updateInfo(userName):
        with open('locked_users.json') as f:
            datalst = json.load(f)
        if userName not in datalst:
            datalst[userName] = {"attempts": 1, "last_attempt": time.time()}
            with open('locked_users.json', 'w') as f:
                json.dump(datalst, f)
        else:
            datalst[userName]["attempts"] += 1
            datalst[userName]["last_attempt"] = time.time()
            with open('locked_users.json', 'w') as f:
                json.dump(datalst, f)
            if datalst[userName]["attempts"] == 3:
                lblMSG4.configure(text="Your Account Has Been Locked Due to Too Many Failed Attemts of Login!", fg=colordict["msg2 color"])

    global user
    user = txtUser.get()
    passw = txtPass.get()
    sql = f'''
        SELECT * FROM users WHERE username="{user}"
    '''
    data = readsql(sql)

    if len(data) == 0:
        lblMSG.configure(text="Username Does Not Exist!", fg=colordict["msg2 color"])
        return
    if isLoggedOut(user):
        lblMSG.configure(text="You're Locked Out! Please Try Again Later!", fg=colordict["msg2 color"])
        lblMSG4.configure(text="")
        return

    sql = f'''
            SELECT * FROM users WHERE username="{user}" and password="{passw}"
        '''
    data = readsql(sql)
    if len(data) == 0:
        lblMSG.configure(text="Wrong Password!", fg=colordict["msg2 color"])
        updateInfo(user)
    else:
        t = datetime.datetime.now().strftime("%H:%M:%S")
        lblMSG.configure(text="Welcome to Your Account!", fg=colordict["msg1 color"])
        with open('users.log', 'a') as f:
            f.write(user+" "+str(date.today())+" "+t+"\n")
        txtUser.delete(0, 'end')
        txtPass.delete(0, 'end')
        btnLogin.configure(state="disabled")
        btnShop.configure(state="active")
        btnCart.configure(state="active")
        if user == "Admin":
            adminPanel()
            log()

def signup():
    colordict = readJson()["Signup Panel"]

    def saveSignup(user, pas, addr):
        sql = f'''
                INSERT INTO users (username, password, address, grade)
                VALUES ("{user}","{pas}","{addr}",0)
            '''
        try:
            cnt.execute(sql)
            cnt.commit()
            return True
        except:
            return False

    def submitVal(user, pas, cpas):
        if user == '' or pas == '' or cpas == '':
            return False, "Empty Fields Error!"
        if pas != cpas:
            return False, "Password Confirmation Incorrect!"
        sql = f'''
                SELECT * FROM users WHERE username="{user}"
            '''
        data = readsql(sql)
        if len(data) > 0:
            return False, "Username Already Exists!"
        pattern = r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$"
        if not re.match(pattern, pas):
            return False, "Invalid Password"
        return True, ""

    def submit():
        user = txtUser1.get()
        pas = txtPass1.get()
        cpas = txtPass2.get()
        addr = txtAddr.get()
        result, msg = submitVal(user, pas, cpas)
        if not result:
            lblMSG2.configure(text=msg, fg=colordict["msg2 color"])
            return
        result = saveSignup(user, pas, addr)
        if not result:
            lblMSG2.configure(text="Something Went Wrong while Connecting to the Database!", fg=colordict["msg2 color"])
        else:
            lblMSG2.configure(text="Signup Went Successfully!", fg=colordict["msg1 color"])
            txtUser1.delete(0, 'end')
            txtPass1.delete(0, 'end')
            txtPass2.delete(0, 'end')
            txtAddr.delete(0, 'end')

    winSignup = tkinter.Toplevel(win)
    winSignup.title('Signup Panel')
    winSignup.geometry('400x400')
    winSignup.configure(bg=colordict["bg color"])

    lblUser1 = tkinter.Label(winSignup, text='Username: ', bg=colordict["bg color"])
    txtUser1 = tkinter.Entry(winSignup, width=18, bg=colordict["txtbox color"])
    lblPass1 = tkinter.Label(winSignup, text='Password: ', bg=colordict["bg color"])
    txtPass1 = tkinter.Entry(winSignup, width=18, bg=colordict["txtbox color"])
    lblPass2 = tkinter.Label(winSignup, text='Password Confirm: ', bg=colordict["bg color"])
    txtPass2 = tkinter.Entry(winSignup, width=18, bg=colordict["txtbox color"])
    lblAddr = tkinter.Label(winSignup, text='Address: ', bg=colordict["bg color"])
    txtAddr = tkinter.Entry(winSignup, width=18, bg=colordict["txtbox color"])

    lblMSG2 = tkinter.Label(winSignup, text='', bg=colordict["bg color"])

    btnSubmit = tkinter.Button(winSignup, text="Submit", width=18, command=submit)

    lst = [lblUser1, txtUser1, lblPass1, txtPass1, lblPass2, txtPass2, lblAddr, txtAddr, lblMSG2, btnSubmit]
    packlist(lst)
    winSignup.mainloop()

def getAllProducts():
    sql = 'SELECT * FROM products'
    return readsql(sql)

def shop():
    colordict = readJson()["Shop Panel"]

    def saveShop(user, pId, pCount):
        pCount = int(pCount)
        pId = int(pId)
        try:
            sql = f'''
                SELECT price FROM products WHERE id={pId}
            '''
            data = readsql(sql)
            pPrice = data[0][0]
            tPrice = pPrice * pCount
            sql = f'''
                SELECT id FROM users WHERE username="{user}"
            '''
            data = readsql(sql)
            uId = data[0][0]
            today = date.today()

            sql = f'''
                 INSERT INTO ShoppingCart (userId, productId, productCount, productPrice, totalPrice, date)
                 VALUES ({uId},{pId}, {pCount},{pPrice},{tPrice},"{today}")                
            '''
            cnt.execute(sql)
            cnt.commit()
            sql = f'''
                 UPDATE products SET number=number-{pCount} WHERE id={pId}
            '''
            cnt.execute(sql)
            cnt.commit()

            lstbox.delete(0, 'end')
            products = getAllProducts()
            for product in products:
                text = f'Id : {product[0]} , Name : {product[1]} , Number : {product[2]} , Price : {product[3]}'
                lstbox.insert('end', text)
            return True
        except:
            return False

    def shopVal(pId, pCount):
        if pId == '' or pCount == '':
            return False, "Empty Fields Error!"
        if not pCount.isdigit() or int(pCount) <= 0:
            return False, "Product Count Must Be a Positive Number!"
        sql = f'''
                SELECT * FROM products WHERE id="{pId}"
            '''
        data = readsql(sql)
        if len(data) == 0:
            return False, "Wrong Product Id!"
        if data[0][2] < int(pCount):
            return False, "Product not Available in Such Quantity!"
        return True, ""

    def buy():
        id = txtId.get()
        num = txtNum.get()
        result, msg = shopVal(id, num)
        if not result:
            lblMSG3.configure(text=msg, fg=colordict["msg2 color"])
            return
        result = saveShop(user, id, num)
        if not result:
            lblMSG3.configure(text="Something Went Wrong while Connecting to the Database!", fg=colordict["msg2 color"])
        else:
            lblMSG3.configure(text="Your Shopping Cart Was Updated Successfully!", fg=colordict["msg1 color"])
            txtId.delete(0, 'end')
            txtNum.delete(0, 'end')
            btnBuy.configure(state="disabled")

    winShop = tkinter.Toplevel(win)
    winShop.title('Shop Panel')
    winShop.geometry('450x450')
    winShop.configure(bg=colordict["bg color"])

    lstbox = tkinter.Listbox(winShop, width=70)
    lstbox.pack(pady=5)
    products = getAllProducts()
    for product in products:
        text = f'Id : {product[0]} , Name : {product[1]} , Number : {product[2]} , Price : {product[3]}'
        lstbox.insert('end', text)

    lblId = tkinter.Label(winShop, text="Product Id: ", bg=colordict["bg color"])
    txtId = tkinter.Entry(winShop, width=18, bg=colordict["txtbox color"])
    lblNum = tkinter.Label(winShop, text='Product Count: ', bg=colordict["bg color"])
    txtNum = tkinter.Entry(winShop, width=18, bg=colordict["txtbox color"])

    lblMSG3 = tkinter.Label(winShop, text="", bg=colordict["bg color"])

    btnBuy = tkinter.Button(winShop, text="BUY!", width=20, command=buy)

    lst = [lblId, txtId, lblNum, txtNum, lblMSG3, btnBuy]
    packlist(lst)
    winShop.mainloop()

def showCart():
    colordict = readJson()["Shopping Cart"]
    sql = f'''
            SELECT id FROM users WHERE username="{user}"
        '''
    data = readsql(sql)
    id = data[0][0]
    sql = f'''
            SELECT * FROM ShoppingCart WHERE userId="{id}"
        '''
    cart = readsql(sql)

    winCart = tkinter.Toplevel(win)
    winCart.title('Shopping Cart')
    winCart.geometry('600x200')
    winCart.configure(bg=colordict["bg color"])

    lstbox = tkinter.Listbox(winCart, width=95)
    lstbox.pack(pady=5)

    for x in cart:
        sql = f'''
            SELECT pname FROM products WHERE id={x[2]}
        '''
        name = readsql(sql)
        text = f'Product Name : {name[0][0]} , Count : {x[3]} , Price : {x[4]} , Total Price : {x[5]} , Date : {x[6]}'
        lstbox.insert('end', text)


cnt = sqlite3.connect('myshop.db')
colordict = readJson()["Shop Project"]
win = tkinter.Tk()
win.title('Shop Project')
win.geometry('400x400')
win.configure(bg=colordict["bg color"])

lblUser = tkinter.Label(win, text='Username: ', bg=colordict["bg color"])
txtUser = tkinter.Entry(win, width=18, bg=colordict["txtbox color"])
lblPass = tkinter.Label(win, text='Password: ', bg=colordict["bg color"])
txtPass = tkinter.Entry(win, width=18, bg=colordict["txtbox color"], show="*")

lblMSG = tkinter.Label(win, text='', bg=colordict["bg color"])
lblMSG4 = tkinter.Label(win, text='', bg=colordict["bg color"])

btnLogin = tkinter.Button(win, text="Login", width=18, command=login)
btnSignup = tkinter.Button(win, text="Signup", width=18, command=signup)
btnShop = tkinter.Button(win, text="Shop Now!", width=18, command=shop, state="disabled")
btnCart = tkinter.Button(win, text="Cart", width=18, command=showCart, state="disabled")

lst = [lblUser, txtUser, lblPass, txtPass, lblMSG, lblMSG4, btnLogin, btnSignup, btnShop, btnCart]
packlist(lst)
win.mainloop()

updateJsonFile()
