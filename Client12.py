import tkinter as tk 
from tkinter import messagebox
from tkinter import ttk
from tkinter import *
from tkinter.ttk import *
from PIL import Image, ImageTk
from tkinter import Entry



    
import socket 
import pickle
import json
import threading


from datetime import date, timedelta
import time


#===== Định nghĩa ======
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
HOST = 1

FONT = ("Arial", 15,"bold")
FORMAT = "utf8"


list=[]
notice =""





#======= Gửi và nhận dữ liệu ======
def SendList(list):
    try:
        for item in list:
            s.sendall(item.encode(FORMAT))
            s.recv(1024)
        msg = "end"
        s.send(msg.encode(FORMAT))
    except:
        messagebox.showerror(title="Thông báo", message="Đã ngắt kết nối đến Server")
        s.close()
        root.destroy()

def ReceiveRes(connect:socket):
    global list
    try:
        msglength = connect.recv(1024).decode(FORMAT)  
        connect.sendall(msglength.encode(FORMAT))

        length = int(msglength)
        rep = ""
        while len(rep) < length:
            rep = rep + connect.recv(1024).decode(FORMAT)
        list = json.loads(rep)   
    except:
        messagebox.showerror(title="Thông báo", message="Đã ngắt kết nối đến Server")
        s.close()
        root.destroy()



#========== Tiến trình ==========

def Connect():
    HOST = entry.get()
    PORT = 65535
    try:
        s.settimeout(1.0)
        s.connect((HOST, PORT))
    except Exception as e:
        messagebox.showerror(title="Thông báo", message="Bạn đã nhập sai địa chỉ IP, kiểm tra lại đi nhé!")
        return  
    Login_GUI()

def SignUp(entry1, entry2, su_gui):
    msg = ["sign up"]
    try:
        SendList(msg)
    except socket.error:
        messagebox.showinfo(title="Thông báo", message="Server đã ngắt kết nối đột ngột")
        s.close()
        root.destroy()
        return
    global notice
    try:
        username = entry1.get()
        password = entry2.get()

        account = [username,password]
        SendList(account)
        notice=s.recv(1024).decode(FORMAT)
        time.sleep(1) 
    except socket.error:
        messagebox.showerror(title="Thông báo", message="Server đã ngắt kết nối")
        s.close()
        root.destroy()
    if notice =="Đăng ký thành công":
        messagebox.showinfo(title="Thông báo", message="Đã đăng ký thành công")
        su_gui.destroy()
        Login_GUI()
    else:   
        messagebox.showerror(title="Thông báo", message="Tài khoản đã tồn tại, bạn vui lòng thử dùng tài khoản khác nhé!")
        su_gui.destroy()
        SignUp_GUI()

def Login(entry1, entry2, log_gui):
    msg = ["login"]
    try:
        SendList(msg)
    except socket.error:
        messagebox.showerror(title="Thông báo", message="Server đã ngắt kết nối đột ngột")
        s.close()
        root.destroy()
        return
    global notice
    try:
        username = entry1.get()
        password = entry2.get()
        account = [username,password]
        SendList(account)
        notice=s.recv(1024).decode(FORMAT)
        time.sleep(1) 
    except socket.error:
        messagebox.showerror(title="Thông báo", message="Đã ngắt kết nối đến Server")
        s.close()
        root.destroy()


    if notice =="Đăng nhập thành công":
        messagebox.showinfo(title="Thông báo", message="Đăng nhập thành công")
        log_gui.destroy()
        Search_GUI()
    else:
        messagebox.showerror(title="Thông báo", message="Bạn đã nhập sai tên đăng nhập hoặc mật khẩu, nhập lại đi nhé!")
        log_gui.destroy()
        Login_GUI()

def Search(entry1, entry2, entry3, tree, search_gui):
    msg = ["search"]
    try:
        SendList(msg)
    except socket.error:
        messagebox.showerror(title="Thông báo", message="Server đã ngắt kết nối")
        s.close()
        root.destroy()
        return
    global list
    tree.delete(*tree.get_children())
    try:
        brand = entry1.get()
        gold_type = entry2.get()
        day = entry3.get()
        if brand == '':
            brand = "blank"
        if gold_type == '':
            gold_type = "blank"
        if day == '':
            day = "blank"
        item = [brand, gold_type, day]
        SendList(item)
        ReceiveRes(s)
        time.sleep(2) 
    except socket.error:
        messagebox.showerror(title="Thông báo", message="Server đã ngắt kết nối đột ngột")
        s.close()
        root.destroy()

    i = 0
    while True:
        if len(list) == 0:
            messagebox.showinfo("Thông báo", "Không tìm thấy dữ liệu cần tra cứu!!!")
            return
        else:
            tree.insert(parent="", index="end",text=" " + list[i]["brand"], values=(list[i]["company"], list[i]["buy"],list[i]["sell"],list[i]["type"],list[i]["updated"]))
            if len(list) - 1 == i:
                break
            i = i + 1

  
        
#========== Giao diện đồ họa người dùng ở Client ==========



def SignUp_GUI():
    su_gui = Toplevel(root)
    su_gui.configure(bg='peru')
    b = Image.open("bg.png")
    fn = ImageTk.PhotoImage(b)
    bg = Label(su_gui, image=fn)
    bg.image = fn
    bg.place(x=0, y=0, relwidth=1, relheight=1)
    su_gui.geometry("450x257")
    su_gui.title("Đăng ký")
    entry1 = tk.Entry(su_gui, width=35)
    label_2 = tk.Label(su_gui, text="ĐĂNG KÝ", font=FONT, fg='#20639b', bg="light yellow")
    entry2 = tk.Entry(su_gui, show="*", width=35, bg='light yellow')
    but_ok = tk.Button(su_gui, text="Đăng ký",foreground="darkslategrey", background="aliceblue", width = 15, command=lambda:SignUp(entry1, entry2, su_gui))
    
    label_2.pack()
    entry1.pack()
    entry2.pack()
    but_ok.pack()
    su_gui.protocol("WM_DELETE_WINDOW", lambda: on_close(su_gui))



def Login_GUI():
    log_gui = Toplevel(root)
    log_gui.configure(bg='peru')
    label_title = tk.Label(log_gui, text="Đăng nhập", font=FONT, fg='#20639b', bg="peru")

    b = Image.open("bg.png")
    fn = ImageTk.PhotoImage(b)
    bg = Label(log_gui, image=fn)
    bg.image = fn
    bg.place(x=0, y=0, relwidth=1, relheight=1)

    entry1 = tk.Entry(log_gui, width=35)
    entry2 = tk.Entry(log_gui, show="*", width=35)
    log_gui.geometry("450x257")
    log_gui.title("Đăng nhập")

    

    regis = tk.Button(log_gui, text="Đăng ký",foreground="darkslategrey", background="aliceblue",width = 15, command=lambda: [destroy_login(log_gui)])
    but_ok = tk.Button(log_gui, text="Đăng nhập",foreground="darkslategrey", background="aliceblue",width = 15, command=lambda:[Login(entry1, entry2, log_gui)])

    label_title.pack()
    entry1.pack()   
    entry2.pack()
    but_ok.pack()
    regis.pack()
    log_gui.protocol("WM_DELETE_WINDOW", lambda: on_close(log_gui))



def Search_GUI():

    search_gui = Toplevel(root)
    
    b = Image.open("backgroundsearch.png")
    fn = ImageTk.PhotoImage(b)
    bg = Label(search_gui, image=fn)
    bg.image = fn
    bg.place(x=0, y=0, relwidth=1, relheight=1)
    search_gui.title("Tra cứu tỉ giá vàng")
    search_gui.geometry("1200x675")
    columns = ('Thương hiệu', 'Tên công ty', 'Mua vào', 'Bán ra', 'Loại vàng', 'Ngày')
    tree = ttk.Treeview(search_gui,  height = 15, columns=columns)
    ttk.Style().configure("tree", background="#383838", 
    foreground="white", fieldbackground="red")
    tree.heading('#0', text='Thương hiệu')
    tree.heading('#1', text='Tên công ty')
    tree.heading('#2', text='Mua vào')
    tree.heading('#3', text='Bán ra')
    tree.heading('#4', text='Loại vàng')
    tree.heading('#5', text='Ngày')

    tree.column('#0', stretch=tk.YES)
    tree.column('#1', stretch=tk.YES)
    tree.column('#2', stretch=tk.YES, anchor = CENTER)
    tree.column('#3', stretch=tk.YES, anchor = CENTER)
    tree.column('#4', stretch=tk.YES, anchor = CENTER)
    tree.column('#5', stretch=tk.YES)
    tree.grid(row=5, columnspan=5, sticky='nsew')
    
    style = ttk.Style()
    style.configure("BW.TLabel", foreground="orangered", background="bisque")

    label1 = ttk.Label(search_gui,text="Thương hiệu:",style="BW.TLabel")
    label1.grid(row=0,column=0)
    entry1 = ttk.Entry(search_gui, width = 50)
    label2 = ttk.Label(search_gui,text="Loại vàng:",style="BW.TLabel")
    label2.grid(row=1,column=0)
    entry2 = ttk.Entry(search_gui, width = 50)
    label3 = ttk.Label(search_gui,text="Ngày(YYYY/MM/DD):",style="BW.TLabel")
    label3.grid(row=0,column=2)
    entry3 = ttk.Entry(search_gui, width = 50)
    days = []
    start_date = date(2021, 12, 7)
    today = date.today()
    delta = today - start_date
    for i in range(delta.days + 1):
        days.append((start_date + timedelta(days=i)).strftime("%Y/%m/%d"))

    butt_search = tk.Button(search_gui, text='Tra cứu',bg="aliceblue", fg="black",
                            command=lambda:  Search(entry1, entry2, entry3, tree, search_gui))
    butt_thoat = tk.Button(search_gui, text="Thoát",bg="aliceblue", fg="black", command=lambda: on_exit())
    entry1.grid(row=0, column=1)
    entry2.grid(row=1, column=1)
    entry3.grid(row=0, column=3)
    butt_search.grid(row=3, column=1)
    butt_thoat.grid(row=3, column=2)


    search_gui.protocol("WM_DELETE_WINDOW", lambda: on_exit())

def destroy_login(log_gui):
    log_gui.destroy()

    SignUp_GUI()

def on_close(frame):
    frame.destroy()

def on_exit():
    try:
         msg = ["exit"]

         SendList(msg)
         time.sleep(1)
         
         s.close()
         root.destroy()

         
    except:
        pass
    finally:
        root.quit()




#=============================================================================
#========== MAIN ==========
root=tk.Tk()
root.geometry("900x487")
root.title("Tra cứu tỉ giá vàng")
root.configure(bg="light yellow")
bard = Image.open("Background.png")
filename = ImageTk.PhotoImage(bard)
background = Label(root, image=filename)
background.image = filename
background.place(x=0, y=0, relwidth=1, relheight=1)


label_title = tk.Label(root,text="Kết nối địa chỉ IP Server", font=FONT,fg='#20639b')
entry = tk.Entry(bg='light yellow')

myButton_connect = tk.Button(text="Kết nối", foreground="darkslategrey", background="aliceblue", width = 10,  command=Connect)
myButton_Exit = tk.Button(text= "Thoát",foreground="darkslategrey", background="aliceblue",width = 10, command=on_exit)  

label_title.place(relx=0.5, rely=0.3, anchor=CENTER)
entry.place(relx=0.5, rely=0.4, anchor=CENTER)
myButton_connect.place(relx=0.5, rely=0.5, anchor=CENTER)
myButton_Exit.place(relx=0.5, rely=0.55, anchor=CENTER)

root.protocol("WM_DELETE_WINDOW", lambda: on_exit())
root.mainloop()


