# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import Context, loader
import datetime

from pygit2 import Repository
from pygit2 import GIT_SORT_TIME, GIT_OBJ_TAG
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
    entries = []
    item = Commit()
    item_cnt = 0;
    loop_cnt = 0;
    skip_cnt = 0;
    entry_per_page = 30

    page = int(page)

    if page <= 1:
        skip_cnt = 0
    elif page > 1:
        skip_cnt = (page-1) * entry_per_page
    else:
        skip_cnt = 0

    #repo = Repository("/var/www/mysite/.git")
    repo = Repository("/home/ibkim/nsserver/M9615R2030/apps_proc/kernel/.git")
    all_refs = repo.listall_references()
    #all_refs = filter(lambda x: x['object'].type != GIT_OBJ_TAG, map(lambda x: {'str': x, 'object':repo.lookup_reference(x)}, all_refs))
    master_ref = repo.lookup_reference("refs/heads/develop")
    print page, skip_cnt, range(0, skip_cnt)

    commit_head = repo[master_ref.oid]

#    if skip_cnt is 0:
#        pass
#    else:
#        for i in range(0,skip_cnt):
#            commit_head = commit_head.parents[0]

    for commit in repo.walk(commit_head.oid, GIT_SORT_TIME):
        if loop_cnt >= entry_per_page:
            break
        item.hexsha = commit.hex
        item.author = commit.author
        item.time   = commit.author.time
        item.message = commit.message
        item.parent1 = commit.parents[0].hex
        if len(commit.parents) > 1:
            item.parent2 = commit.parents[1].hex

        entries.append(copy.copy(item))
        loop_cnt += 1

    tpl = loader.get_template('commit_list.html')
    ctx = Context( {'refs': all_refs, 'commits': entries} )
    return HttpResponse(tpl.render(ctx))

class Diff:
    pass

def diff(request, sha=0):
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
