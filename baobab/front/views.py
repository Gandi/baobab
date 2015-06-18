# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.views.decorators.gzip import gzip_page
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers


@gzip_page
@cache_page(3600)
@vary_on_headers('Accept-Encoding')
def index(request):
    resp = render(request, 'index.html')
    resp['X-UA-Compatible'] = 'IE=edge,chrome=1'

    return resp
