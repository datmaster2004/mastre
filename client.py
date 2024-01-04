
import socket
import ssl

def menu_client():
    print("1. Shutdown")
    print("2. ScreenShot")
    print("3. Keystroke")
    print("4. App running")
    print("5. Open Chrome")
    print("0. Exit")
    print("SELECT: ")


IPserver = input("IP Server: ")
Portserver = int(input("PORT Server: "))
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((IPserver, Portserver))
if client:
    while True:
        menu_client()
        choose = int(input())
        match choose:
            case 5: client.sendall("start chrome".encode())
            case 0: client.sendall("0".encode())
        if(choose == 0): break
client.close()