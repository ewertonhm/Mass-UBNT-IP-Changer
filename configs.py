from Cryptodome.Cipher import AES
import configparser
import pathlib
import inspect
import os, sys
import base64
import getpass
import dload
from datetime import datetime


def download_chromedriver():
    return dload.save_unzip(
        'https://chromedriver.storage.googleapis.com/95.0.4638.69/chromedriver_win32.zip',
        extract_path=find_path(),
        delete_after=True
    )

def find_path():
    filename = sys.argv[0]
    pythonpath = sys.executable

    path = ''

    if os.path.split(sys.argv[0])[1][-2:] == 'py':
        path = sys.executable[0:-23]
    else:
        if filename[-3:] == 'exe':
            path = pythonpath[:-len(filename)]
        else:
            path = pythonpath[:-(len(filename)+4)]
    return path

def read_file(file_name):
    f = open(file_name, 'r')
    values = f.readlines()
    return values

def write_to_sucess(host):
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")

    string = current_time + ' : ' + host
    path = find_path()
    filename = path + 'changed.ini'
    # Open the file in append & read mode ('a+')
    with open(filename, "a+") as file_object:
        # Move read cursor to the start of file.
        file_object.seek(0)
        # If file is not empty then append '\n'
        data = file_object.read(100)
        if len(data) > 0:
            file_object.write("\n")
        # Append text at the end of file
        file_object.write(string)

def write_to_fail(host):
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")

    string = current_time + ' : ' + host
    path = find_path()
    filename = path + 'fail.ini'
    # Open the file in append & read mode ('a+')
    with open(filename, "a+") as file_object:
        # Move read cursor to the start of file.
        file_object.seek(0)
        # If file is not empty then append '\n'
        data = file_object.read(100)
        if len(data) > 0:
            file_object.write("\n")
        # Append text at the end of file
        file_object.write(string)

def write_to_log(string):
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")

    string = current_time + ' : ' + string
    print(string)
    path = find_path()
    filename = path + 'log.ini'
    # Open the file in append & read mode ('a+')
    with open(filename, "a+") as file_object:
        # Move read cursor to the start of file.
        file_object.seek(0)
        # If file is not empty then append '\n'
        data = file_object.read(100)
        if len(data) > 0:
            file_object.write("\n")
        # Append text at the end of file
        file_object.write(string)