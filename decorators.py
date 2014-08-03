from functools import wraps
from threading import Thread

#TODO timed, jsonp http://flask.pocoo.org/snippets/category/decorators/

def async(f):
    def wrapper(*args, **kwargs):
        thread = Thread(target=f, args=args, kwargs=kwargs)
        thread.start()
    return wrapper