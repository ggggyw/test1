import webbrowser
import subprocess
import socket
import time

def runserver():
    server = subprocess.Popen(['python', 'manage.py', 'runserver', '127.0.0.1:8000'])
    return server

def open_in_browser():
    webbrowser.open('http://127.0.0.1:8000')

def check_server(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((host, port)) == 0

if __name__ == "__main__":
    server = runserver()
    while not check_server('127.0.0.1', 8000):
        time.sleep(1)
    open_in_browser()