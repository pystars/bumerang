# -*- coding: utf-8 -*-
"""
remember, signals and receivers usually connected in bot of models.py
"""
from __future__ import division
from collections import defaultdict
from cStringIO import StringIO

from PIL import Image
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from bumerang.apps.events.signals import juror_added

from bumerang.apps.utils.email import send_single_email
from bumerang.apps.utils.functions import image_crop_rectangle_center


Profile = get_user_model()


def notify_admins_about_event_request(sender, **kwargs):
    event = kwargs['event']
    to = dict(settings.MANAGERS).values()
    ctx = {
        'header': u'''Заявка на регистрацию события "{0} {1}"'''.format(
            event.get_type_display(), event),
        'subject': u'''Заявка на регистрацию события "{0} {1}"'''.format(
            event.get_type_display(), event),
        'event': event
    }
    send_single_email(
        "events/emails/notify_managers_about_event_request.html", ctx,
        ctx['subject'], settings.EMAIL_NOREPLY_ADDR, to)


def notify_event_owner_about_approve(sender, **kwargs):
    event = kwargs['event']
    ctx = {
        'header': u'"{0} {1} одобрен"'.format(event.get_type_display(), event),
        'subject': u'"{0} {1} одобрен"'.format(event.get_type_display(), event),
        'event': event
    }
    send_single_email("events/emails/notify_event_owner_about_approval.html",
                      ctx, ctx['subject'], settings.EMAIL_NOREPLY_ADDR,
                      [event.owner.username])


def notify_winners(sender, **kwargs):
    event = kwargs['event']
    winners = defaultdict(list)
    from models import VideoNomination, Participant
    video_nominations = VideoNomination.objects.filter(
        nomination__event=event, result__isnull=False).order_by(
            'nomination__sort_order')
    for video_nomination in video_nominations:
        winners[video_nomination.participant_video.participant_id].append(
            video_nomination)
    for winner, video_nominations in winners.iteritems():
        ctx = dict(
            header=u'Поздравляем! Вы стали победителем события "{0} {1}".'
                   u''.format(event.get_type_display(), event),
            subject=u'Вы победитель {0}'.format(event),
            video_nominations=video_nominations,
            event=event
        )
        participant = Participant.objects.get(pk=winner)
        send_single_email("events/emails/event_winners_congratulation.html",
                          ctx, ctx['subject'], settings.EMAIL_NOREPLY_ADDR,
                          [participant.owner.username])


def notify_participant_about_review(sender, **kwargs):
    participant = kwargs['participant']
    videos = participant.participant_videos.filter(is_accepted=True)
    ctx = {
        'header': u'Ваша заявка рассмотрена к участию в событии {0}'
                  u' были приняты следующие фильмы:'.format(participant.event),
        'subject': u'Заявка на участие в событии обработана',
        'videos': videos,
        'participant': participant
    }
    send_single_email("events/emails/notify_participant_about_review.html", ctx,
                      ctx['subject'], settings.EMAIL_NOREPLY_ADDR,
                      [participant.owner.username])


def notify_event_owner_about_participant(sender, **kwargs):
    participant = kwargs['instance']
    if not participant.is_accepted:
        ctx = {
            'header': u'Новая заявка на участие в событии',
            'subject': u'Новая заявка на участие в событии',
            'participant': participant
        }
        send_single_email(
            "events/emails/notify_event_owner_about_participant.html",
            ctx, ctx['subject'], settings.EMAIL_NOREPLY_ADDR,
            [participant.event.owner.username])


def notify_jurors_about_participant(sender, **kwargs):
    participant = kwargs['participant']
    videos = participant.participant_videos.filter(is_accepted=True)
    ctx = {
        'header': u'Новые работы от участников для выставления оценок',
        'subject': u'Новые работы от участников для выставления оценок',
        'videos': videos,
        'participant': participant
    }
    send_single_email(
        "events/emails/notify_jurors_about_participant.html", ctx,
        ctx['subject'], settings.EMAIL_NOREPLY_ADDR,
        participant.event.juror_set.values_list('email', flat=True))


def relate_juror_and_profile(sender, **kwargs):
    if kwargs['raw']:
        return
    instance = kwargs['instance']
    try:
        instance.user = Profile.objects.get(username=instance.email)
        juror_added.send(None, juror=instance, created=False, password='')
    except Profile.DoesNotExist:
        title = u'{0} {1} {2}'.format(
            instance.info_second_name,
            instance.info_name,
            instance.info_middle_name
        )
        profile = Profile(
            username=instance.email,
            title=title,
            info_second_name=instance.info_second_name,
            info_name=instance.info_name,
            info_middle_name=instance.info_middle_name
        )
        password = Profile.objects.make_random_password()
        profile.set_password(password)
        profile.save()
        instance.user_id = profile.id

        instance.min_avatar.seek(0)
        minified_image = Image.open(instance.min_avatar)
        minified_image = image_crop_rectangle_center(minified_image)
        minified_image.thumbnail((125, 125), Image.ANTIALIAS)
        # reinitialize memory file
        memory_file = StringIO()
        minified_image.save(memory_file, 'jpeg')
        memory_file.seek(0)

        profile.min_avatar.save(
            '{id}-min-avatar.jpg'.format(id=profile.id),
            ContentFile(memory_file.read())
        )
        profile.save()
        juror_added.send(None, juror=instance, created=True, password=password)


def notify_juror_about_registration(sender, **kwargs):
    juror = kwargs['juror']
    from models import ParticipantVideo

    videos = ParticipantVideo.objects.filter(
        is_accepted=True,
        participant__in=juror.event.participant_set.values_list(
            'id', flat=True))
    ctx = {
        'header': u'Вы добавлены в жюри события',
        'subject': u'Вы добавлены в жюри события',
        'juror': juror
    }
    if videos.exists():
        ctx['videos'] = videos
    if kwargs['created']:
        ctx['password'] = kwargs['password']
        send_single_email(
            "events/emails/juror_registration.html", ctx,
            ctx['subject'], settings.EMAIL_NOREPLY_ADDR, [juror.email])
    else:
        send_single_email(
            "events/emails/juror_invited.html", ctx,
            ctx['subject'], settings.EMAIL_NOREPLY_ADDR, [juror.email])
