# -*- coding: utf-8 -*-
from django.dispatch.dispatcher import Signal

approve_event = Signal(['event'])
winners_public = Signal(['event'])
event_created = Signal(['event'])
participant_reviewed = Signal(['participant'])
juror_added = Signal(['juror', 'created', 'password'])
