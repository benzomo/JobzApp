import xlwings as xw
import pandas as pd
import numpy as np
import indeed

def hello_xlwings():
    wb = xw.Book.caller()
    wb.sheets[0].range("A1").value = "Hello xlwings!"


@xw.func
def hello(name):
    return "hello {0}".format(name)


@xw.func
@xw.arg('old', np.array, doc='Old Jobs')
@xw.ret(expand='table')
def get_indeed(old):

    return indeed.get_jobs(old)


@xw.func
@xw.arg('test1', np.array, doc='xyz')
@xw.ret(expand='table')
def test(test1):

    return pd.DataFrame(test1)