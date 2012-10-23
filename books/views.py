
# Create your views here.
import os, sys
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

    try:
        repo = Repo("/home/ibkim/project/python/mysite", odbt=GitCmdObjectDB)
    except NoSuchPathError:
        repo = Repo("/home/ibkim/project/linux", odbt=GitCmdObjectDB)
    commits = repo.iter_commits('master', max_count = entry_per_page, skip = skip_cnt, author='ilbong kim', grep='')

    commits = map(lambda x: {'hexsha': x.hexsha, 'author': x.author, 'summary': x.summary, 'committed_date': datetime.datetime.fromtimestamp(x.committed_date), 'message': x.message}, commits)

    prev_page_num = page - 1
    next_page_num = page + 1

    if prev_page_num <= 0:
        prev_page_num = 1
    tpl = loader.get_template('commit_list.html')
    ctx = Context( {'refs': repo.heads, 'commits': commits, 'prev_page': prev_page_num, 'next_page': next_page_num,} )
    return HttpResponse(tpl.render(ctx))

def diff(request, sha=''):
    try:
        repo = Repo("/home/ibkim/project/python/mysite", odbt=GitCmdObjectDB)
    except NoSuchPathError:
        repo = Repo("/home/ibkim/project/linux", odbt=GitCmdObjectDB)

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

def makedocs(request, sha=''):
    from docx import *
    relationships = relationshiplist()
    document = newdocument()
    docbody = document.xpath('/w:document/w:body', namespaces=nsprefixes)[0]
    docbody.append(heading('''Welcome to Python's docx module''',1)  )
    docbody.append(heading('Make and edit docx in 200 lines of pure Python',2))
    docbody.append(paragraph('The module was created'))
    for point in ['''COM automation''','''.net or Java''','''Automating OpenOffice or MS Office''']:
        docbody.append(paragraph(point,style='ListNumber'))
    docbody.append(paragraph('''For those of us who prefer something simpler, I made docx.'''))
    docbody.append(heading('Making documents',2))
    #docbody.append(paragraph('''The docx module has the following features:'''))
    
    repo = Repo("/home/ibkim/project/python/mysite", odbt=GitCmdObjectDB)

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
        paratext = [(htmldiff, 'h'),]
        docbody.append(paragraph(paratext))        

    for entry in diff.iter_change_type('A'):
        AddDiff.append(entry)
    for entry in diff.iter_change_type('D'):
        DelDiff.append(entry)
    for entry in diff.iter_change_type('R'):
        ReDiff.append(entry)

    tpl = loader.get_template('diff.html')
    ctx = Context( {'add': AddDiff, 'del': DelDiff, 'rename': ReDiff, 'modify': ModDiff} )

    docbody.append(pagebreak(type='page', orient='portrait'))
    coreprops = coreproperties(title='Python docx demo',subject='A practical example of making docx from Python',creator='Mike MacCana',keywords=['python','Office Open XML','Word'])
    appprops = appproperties()
    contenttypes = contenttypes()
    websettings = websettings()
    wordrelationships = wordrelationships(relationships)
    savedocx(document,coreprops,appprops,contenttypes,websettings,wordrelationships,'diff.docx')
    
    return HttpResponse(tpl.render(ctx))    
