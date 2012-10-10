# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import Context, loader
import datetime

from pygit2 import Repository
from pygit2 import GIT_SORT_TIME
import copy

from diff2html import parse_from_memory

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

class Commit:
    pass

def commits(request, page=1):
    commit = []
    item = Commit()
    repo = Repository("/var/www/mysite/.git")
    #repo = Repository("/home/ibkim/nsserver/M9615R2030/apps_proc/kernel/.git")
    all_refs = repo.listall_references()
    master_ref = repo.lookup_reference("refs/heads/master")
    commit_head = repo[master_ref.oid]

    item.hexsha = commit_head.hex
    item.author = commit_head.author
    item.time   = commit_head.author.time
    item.message = commit_head.message

    commit.append(copy.copy(item))

    commit_head = commit_head.parents[0]

    item.hexsha = commit_head.hex
    item.author = commit_head.author
    item.time   = commit_head.author.time
    item.message = commit_head.message

    commit.append(copy.copy(item))

    tpl = loader.get_template('commit_list.html')
    ctx = Context( {'refs': all_refs, 'commits': commit} )
    return HttpResponse(tpl.render(ctx))

class Diff:
    pass

def diff(request, page=1):
    repo = Repository("/var/www/mysite/.git")
    dev = repo.head
    t0 = dev.tree
    t1 = dev.parents[0].tree
    diff = t1.diff(t0)

    # formatting
    Diff.patch = parse_from_memory(diff.patch, True, True)

    tpl = loader.get_template('diff.html')
    ctx = Context( {'diff': Diff,} )
    return HttpResponse(tpl.render(ctx))
