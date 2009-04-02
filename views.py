#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response

from apps.tree.models import *


def index(req):
	return render_to_response("index.html",
	    { "trees": Tree.objects.all(), "t": Tree.objects.all()[0] },
	    context_instance=RequestContext(req))