
# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import Context, loader
import datetime

from git import *
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
    entry_per_page = 10

    page = int(page)

    if page <= 1:
        skip_cnt = 0
    elif page > 1:
        skip_cnt = (page-1) * entry_per_page
    else:
        skip_cnt = 0

    repo = Repo("/home/ibkim/nsserver/M9615R2030/apps_proc/kernel", odbt=GitCmdObjectDB)
    commits = repo.iter_commits('develop', max_count = entry_per_page, skip = skip_cnt)

    prev_page_num = page - 1
    next_page_num = page + 1
    if prev_page_num <= 0:
        prev_page_num = 1
    tpl = loader.get_template('commit_list.html')
    ctx = Context( {'refs': repo.heads, 'commits': commits, 'prev_page': prev_page_num, 'next_page': next_page_num,} )
    return HttpResponse(tpl.render(ctx))

def diff(request, sha=''):
    repo = Repo("/home/ibkim/nsserver/M9615R2030/apps_proc/kernel", odbt=GitCmdObjectDB)

    try:
        commit = repo.commit(sha)
    except BadObject:
        tpl = loader.get_template('error.html')
        ctx = Context( {'error': 'Bad ObjectError',} )
        return HttpResponse(tpl.render(ctx))

    diff = commit.diff( commit.hexsha + '~1', None, True)
    AddDiff = []
    DelDiff = []
    ReDiff = []
    ModDiff = []
    # HTML formatting
    for entry in diff.iter_change_type('M'):
        if entry.deleted_file or entry.new_file or entry.renamed:
            continue
        htmldiff = parse_from_memory(entry.diff, True, True)
        ModDiff.append({'diff': htmldiff,})

    for entry in diff.iter_change_type('A'):
        AddDiff.append(entry)
    for entry in diff.iter_change_type('D'):
        DelDiff.append(entry)
    for entry in diff.iter_change_type('R'):
        ReDiff.append(entry)

    tpl = loader.get_template('diff.html')
    ctx = Context( {'add': AddDiff, 'del': DelDiff, 'rename': ReDiff, 'modify': ModDiff} )
    return HttpResponse(tpl.render(ctx))
