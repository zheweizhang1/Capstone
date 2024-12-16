import os
from ctypes import cdll

if os.name == 'nt':  # Windows
    lib = cdll.LoadLibrary('./libfoo.dll')
elif os.name == 'posix':  # macOS or Linux
    lib = cdll.LoadLibrary('./libfoo.so')

class Foo:
    def __init__(self):
        self.obj = lib.Foo_new()

    def bar(self):
        lib.Foo_bar(self.obj)
