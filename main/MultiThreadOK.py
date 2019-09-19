import sqlite3
import threading
from queue import Queue


class MultiThreadOK(threading.Thread):
    """Slightly modified version of sqlite multithread support by Louis RIVIERE"""

    def __init__(self, db):
        super(MultiThreadOK, self).__init__()
        self.db = db
        self.reqs = Queue()
        self.start()

    def run(self):
        cnx = sqlite3.connect(self.db)
        cursor = cnx.cursor()
        while True:
            req, arg, res = self.reqs.get()
            if req == '--commit--':
                cnx.commit()
            if req == '--close--':
                break
            try:
                cursor.execute(req, arg)
            except:
                pass
            if res:
                for rec in cursor:
                    res.put(rec)
                res.put('--no more--')
        cursor.close()
        cnx.commit()
        cnx.close()

    def execute(self, req, arg=None, res=None):
        self.reqs.put((req, arg or tuple(), res))

    def select(self, req, arg=None):
        res = Queue()
        self.execute(req, arg, res)
        while True:
            rec = res.get()
            if rec == '--no more--':
                break
            yield rec

    def commit(self):
        self.execute('--commit--')

    def close(self):
        self.execute('--close--')