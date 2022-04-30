from socket import *
import json
from urllib.request import urlopen
import threading
import pickle
import time
from datetime import datetime
import tkinter as tk 
from tkinter import messagebox
from tkinter import ttk
from tkinter import *
from tkinter.ttk import *
from PIL import ImageTk, Image
PORT= 65535
FORMAT="utf8"
LARGE_FONT = ("Inter", 14, "bold")


#Lấy dữ liệu từ web xuống
def GetDataFromWeb():
    url = "https://tygia.com/json.php?ran=0&rate=0&gold=1&bank=VIE"
    resp = urlopen(url)
    data = json.loads(resp.read())
    return data
def SaveDataToJson(data):
    with open('GiaVang.json','w', encoding="utf-8") as jsonfile:
        json.dump(data,jsonfile,ensure_ascii=False)


#Xử lý đăng nhập, đăng ký, thêm dữ liệu tài khoản vào file JSON
def InsertNewAcc(data,file_name):
    with open(file_name,'r+') as DSTK:
        datajson=json.load(DSTK)
        datajson["Login"].append(data)
        DSTK.seek(0)
        json.dump(datajson,DSTK)


def SignUp(acc,client):
    with open("DSTK.json",'r') as DSTK:
        account=json.load(DSTK)
    for i in account["Login"]:
        if(acc[0]==i["TaiKhoan"]):
            noti="Không thành công"
            client.sendall(noti.encode(FORMAT))
            return 0
    TaiKhoan = {"TaiKhoan":acc[0].__str__(),
               "MatKhau": acc[1].__str__() }

    InsertNewAcc(TaiKhoan,"DSTK.json")
    noti="Đăng ký thành công"
    print(noti)
    client.sendall(noti.encode(FORMAT))
    return 1

def Login(acc,client):
    with open("DSTK.json",'r') as DSTK:
        account=json.load(DSTK)
    for i in account["Login"]:
        if(acc[0]==i["TaiKhoan"] and acc[1]==i["MatKhau"]):
            noti="Đăng nhập thành công"
            client.sendall(noti.encode(FORMAT))
            return 1
    client.sendall("0".encode(FORMAT))
    return 0
 
 #Xử lý tìm kiếm
def Search(client, item):
    if item==[]:
        return
    brand, gold_type, day = item
    day1 = day
    if day!="blank":
        day1 = datetime.strptime(day, "%Y/%m/%d").strftime('%Y%m%d')
    with open("GiaVang.json", "r", encoding="utf-8") as GVfile:
        data=json.load(GVfile)
    check = 0
    Lresult=[]
    for i in data["golds"]:
        if day1==i["date"]:
            data1 = i["value"]
            if brand != "blank" and gold_type != "blank":
                for j in data1:
                    if j["brand"].lower() == brand.lower() and j["type"].lower() == gold_type.lower():
                        Lresult.append(j)
            elif brand!="blank" and gold_type =="blank":
                for j in data1:
                    if j["brand"].lower() == brand.lower():
                        Lresult.append(j)
            elif brand=="blank" and gold_type!="blank":
                for j in data1:
                    if j["type"].lower() == gold_type.lower():
                        Lresult.append(j)
            else:
                for j in data1 :
                   Lresult.append(j)
        elif day=="blank":
            data1=i["value"]
            if brand!="blank" and gold_type !="blank":
                for j in data1:
                    if j["brand"].lower() == brand.lower() and j["type"].lower() == gold_type.lower():
                        Lresult.append(j)
            elif brand!="blank" and gold_type=="blank":
                for j in data1:
                    if j["brand"].lower() == brand.lower():
                        Lresult.append(j)
            elif brand=="blank" and gold_type!="blank":
                for j in data1:
                    if j["type"].lower() == gold_type.lower():
                        Lresult.append(j)
            else:
                for j in data1 :
                   Lresult.append(j)

    SendResultSearch(client,Lresult)
  
def SendResultSearch(client, list):
    msg=json.dumps(list,ensure_ascii=False)
    lengthdata = len(msg).__str__()
    try:
        client.sendall(lengthdata.encode(FORMAT))
        client.recv(1024)
        client.sendall(msg.encode(FORMAT))
    except:
        client.close()
        return
#Nhận dữ liệu từ client
def ReceiveFromClient(socket):
    acc=[]
    try:
        item=socket.recv(1024).decode(FORMAT)
        while item!="end":
            acc.append(item)
            socket.sendall(item.encode(FORMAT))
            item=socket.recv(1024).decode(FORMAT)
    except:
        return [] 
    return acc
#Client thoát thì xóa khỏi ds
def ClientExit(client, add):
    num_client.remove((client,add))
    client.close()
#Xử lý lệnh
def HandleClient(client,add):
    while True:
        try:
            rep=ReceiveFromClient(client)
        except:
            client.close()
            break
        rep[0].lower()
        print(rep)
        if rep[0]=="sign up":
            taikhoan=ReceiveFromClient(client)
            SignUp(taikhoan,client)
        elif rep[0]=="login":
            taikhoan=ReceiveFromClient(client)
            if Login(taikhoan,client)==1:
                num_client.append((client,add))
        elif rep[0]=="search":
            item=ReceiveFromClient(client)
            Search(client,item)
        elif rep[0] == "exit":
            ClientExit(client, add)
            break
        else:
            noti=" Nhập lệnh không hợp lệ"
            client.sendall(noti.encode(FORMAT))

#Thoát server
def ServerExit(): 
    for client, add in num_client:
        try:
            noti = "Server đã đóng"
            client.sendall(noti.encode(FORMAT))
            client.close()
        except:
            pass
    app.destroy()
    s.close()
#Chạy server   
def RunServer():
    try:
        while True:
            #Accept connect
            client, add = s.accept()
            # Processing request
            thr = threading.Thread(target=HandleClient, args=(client, add))
            thr.daemon = True
            thr.start()
            threads.append(thr)
    except KeyboardInterrupt:
        print('Stopped')
        s.close()
    finally:
        for thr in threads:
            thr.join()
        for client, add in num_client:
            client.close()
        s.close()

#=============GUI===============
class App(tk.Tk):
    def Run_Server(self):
        s_thread = threading.Thread(target=RunServer)
        s_thread.daemon = True
        s_thread.start()
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.title("Server Host")
        self.geometry("1000x500")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.resizable(width=False, height=False)

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=5)
        container.grid_columnconfigure(0, weight=5)

        threading.Thread(target=self.Run_Server).start()
        self.frames = {}
        for F in (StartPage, HomePage):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
    
        self.ShowFrame(StartPage)

    def ShowFrame(self, container):
        frame = self.frames[container]
        if container == StartPage:
            self.geometry("800x400")
        if container == HomePage:
            self.geometry("800x400")
        else:
            self.geometry("800x400")
        frame.tkraise()

    
    def on_closing(self):
        global quit
        if messagebox.askokcancel("Quit", "Bạn có muốn thoát?"):
            quit = True
            self.destroy()



    def ServerLogin(self, CFrame):

        UN = CFrame.entry_user.get()
        PW = CFrame.entry_pswd.get()

        if UN == "server" and PW == "hcmus":
            self.ShowFrame(HomePage)
            CFrame.label_errorlogin["text"] = ""
        else:
            CFrame.label_errorlogin["text"] = "Tài Khoản hoặc Mật Khẩu sai! Vui lòng thử lại"

class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        Ima2 = Image.open("s_background.png")
        filename = ImageTk.PhotoImage(Ima2)
        Background2 = Label(self, image=filename)
        Background2.image = filename
        Background2.place(x=0, y=0, relwidth=1, relheight=1)

        label_title = tk.Label(self, text="\nLOG IN FOR SEVER\n",bg="light blue").place(x= 367,y=125)

        label_username = tk.Label(self, text="USERNAME: ",bg="light blue").place(x=250,y=195)
        label_password = tk.Label(self, text="PASSWORD: ",bg="light blue").place(x=250,y=225)
        self.label_errorlogin = tk.Label(self, text="", bg="#3399FF", fg='red')
        self.entry_user = tk.Entry(self, width=30, bg="light blue")
        self.entry_pswd = tk.Entry(self, width=30, bg="light blue")
        button_login = tk.Button(self, text="LOG IN", bg="#33CCCC", fg='white',
                               command=lambda: controller.ServerLogin(self))
        self.entry_pswd.place(x=329,y=225)
        self.entry_user.place(x=329,y=195)
        button_login.place(x=375,y=268)
        button_login.configure(width=10)
        self.label_errorlogin.place(x=359,y=248)
class HomePage(tk.Frame):


    def __init__(self, parent, controller):
        
        tk.Frame.__init__(self, parent)
        Ima = Image.open("s_bg.jpeg")
        filename = ImageTk.PhotoImage(Ima)
        Background = Label(self, image=filename)
        Background.image = filename
        Background.place(x=0, y=0, relwidth=1, relheight=1)


        self.displayserver = tk.Frame(self)
        self.data = tk.Listbox(self.displayserver, height=20,
                               width=40,
                               bg='#CC6600',
                               activestyle='dotbox',
                               font="Roboto",
                               fg='black')

        Refresh = tk.Button(self, text="REFRESH", bg="#00CC99", fg='white',command=self.Update_Client)
        LogOut = tk.Button(self, text="ĐĂNG XUẤT", bg="#00CC99", fg='white', command=lambda: controller.ShowFrame(StartPage))
        ShutDown = tk.Button(self, text="THOÁT", bg="#CC3300", fg='white', command=ServerExit)


        Refresh.place(x=600, y=100)
        Refresh.configure(width=10)
        LogOut.place(x=600, y=160)
        LogOut.configure(width=10)
        ShutDown.place(x=600, y=220)
        ShutDown.configure(width=10)





        self.displayserver.pack_configure()
        self.scroll = tk.Scrollbar(self.displayserver)
        self.data.config(yscrollcommand=self.scroll.set)
        self.scroll.config(command=self.data.yview)
        self.data.pack(side="top",fill="both",padx=10,pady=100)
      
        label_name=tk.Label(self,text=TenServer,font=LARGE_FONT, fg='white',bg="#3366CC").place(x=200,y=350)
        label_title = tk.Label(self, text="\n DANH SÁCH CLIENT KẾT NỐI\n", font=LARGE_FONT, fg='white',
                               bg="#3366CC").place(x=260, y=25)

    def ServerExit(): 
        for client,add in num_client:
            noti = "Server đã đóng"
            client.sendall(noti.encode(FORMAT))
            sclient.close()
            app.destroy()
            s.close()
    def Update_Client(self):
        self.data.delete(0, len(num_client))
        for i in range(len(num_client)):
            display=num_client[i][1].__str__() + "is connected to server"
            self.data.insert(i, display)
#================
host_name = gethostname()    
HOST = gethostbyname(host_name)
s = socket(AF_INET, SOCK_STREAM)

s.bind((HOST, PORT))
TenServer ="Server: "+ HOST.__str__()+ " Port:" + PORT.__str__()+ " is running" 

s.listen()
# Các luồng và client
threads = []
num_client = []
SaveDataToJson(GetDataFromWeb())

app=App()
app.mainloop()
s.close()