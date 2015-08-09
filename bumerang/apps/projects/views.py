# -*- coding: utf-8 -*-
from django.views.generic import ListView, DetailView

from .models import Project


class ProjectListView(ListView):
    model = Project


class ProjectDetailView(DetailView):
    model = Project
