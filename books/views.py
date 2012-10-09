# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import Context, loader
import datetime

from pygit2 import Repository
from pygit2 import GIT_SORT_TIME

from books.models import Book

def hello(request):
    return HttpResponse("Hello world")

def time(request, t):
    try:
        hours = int(t)
    except ValueError:
        raise Http404()
    date = datetime.datetime.now() + datetime.timedelta(hours)
    return render_to_response('time.html', locals())

def books(request, page=1):
    books = Book.objects.all()
    tpl = loader.get_template('books.html')
    ctx = Context( {'books': books,} )
    return HttpResponse(tpl.render(ctx))

def commits(request, page=1):
    repo = Repository("/home/ibkim/pygit2/.git")
    #dev = repo.heads.develop
    commit = repo.walk(repo.head.oid, GIT_SORT_TIME)
    tpl = loader.get_template('commit_list.html')
    ctx = Context( {'commits': commit,} )
    return HttpResponse(tpl.render(ctx))

