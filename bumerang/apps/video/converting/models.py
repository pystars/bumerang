# -*- coding: utf-8 -*-
from django.db import models

from bumerang.apps.utils.models import nullable, choices


class ConvertOptions(models.Model):
    """
    class for manage video converting options for HandBrakeCLI
     -t 1 -c 1 -o ""  -f mp4 -w 720 -l 416 -e x264 -b 900 -r 25 -a 1 -E faac -6
      stereo -R 44.1 -B 128 -D 0.0
       -x ref=2:bframes=2:subq=6:mixed-refs=0:weightb=0:8x8dct=0:trellis=0
    """

    BITRATE_CHOICES = choices(64, 96, 128, 160)
    PRESET_CHOICES = choices('Normal', 'High Profile', 'Classic')
    RATE_CHOICES = choices("5", "10", "12", "15", "23.976", "24", "25", "29.97")
    codec = 'x264'
    channels = 'stereo'

    title = models.CharField('title', max_length=20)
    sample_rate = models.FloatField('audio sampling frequency', **nullable)
    abitrate = models.PositiveIntegerField('audio bit rate',
        help_text='kbits/s (default like source)',
        choices=BITRATE_CHOICES, **nullable)
    preset = models.CharField('x264 preset', max_length=20,
        choices=PRESET_CHOICES)
    vbitrate = models.PositiveIntegerField('video bit rate',
        help_text='(bit/s)', **nullable)
    frame_rate = models.CharField('frame rate', max_length=10,
        help_text='(Hz value)', choices=RATE_CHOICES, **nullable)
    width = models.PositiveIntegerField('width')
    height = models.PositiveIntegerField('height', **nullable)
    quality = models.PositiveIntegerField('quality lvl',
        help_text='between 1 (excellent quality) and 31 (worst)', **nullable)
    x264opts = models.CharField('x264 options', max_length=400,
    default='ref=2:bframes=2:subq=6:mixed-refs=0:weightb=0:8x8dct=0:trellis=0',
        **nullable)

    def __unicode__(self):
        return ' '.join(self.as_commandline())

    def as_commandline(self):
        args = [
            '-t', '1',
            '-f', 'mp4',
            '-w', str(self.width),
            '-e', self.codec,
            '-b', str(self.vbitrate),
            '-r', self.frame_rate,
            '-a', '1',
            '-E', 'faac',
            '-6', self.channels,
            '-R', str(self.sample_rate),
            '-B', str(self.abitrate),
            '-D', '0.0',
            '-x', self.x264opts,
        ]
        if self.height:
            args += ['-l', str(self.height)]
        if self.preset:
            args += ['-Z', self.preset]
        return args

    def update(self, media_info):
        video = media_info['Video']
        audio = media_info.get('Audio', {})
        if video['Width'] < self.width:
            self.width = video['Width']
        self.height = int(self.width / float(video['Width']) / video['Height'])
        vbitrate = (video['BitRate_Maximum'] or video['BitRate']) / 1000
        if self.vbitrate > vbitrate:
            self.vbitrate = vbitrate
        if float(self.frame_rate) > video['FrameRate']:
            self.frame_rate = str(video['FrameRate'])
        if audio:
            if audio['SamplingRate']:
                sample_rate = audio['SamplingRate'] / 1000
                if self.sample_rate > sample_rate:
                    self.sample_rate = sample_rate
            if audio['BitRate_Maximum'] or audio['BitRate']:
                abitrate = (audio['BitRate_Maximum'] or audio['BitRate']) / 1000
                if self.abitrate > abitrate:
                    self.abitrate = abitrate
            if audio['Channel(s)'] == 1:
                self.channels = 'mono'

    def adjust(self, media_info):
        video = media_info['Video']
        audio = media_info.get('Audio', {})
        if video['Width'] < self.width:
            self.width = video['Width']
        self.height = int(self.width * video['Height'] / float(video['Width']))
        vbitrate = (video['BitRate_Maximum'] or video['BitRate']) / 1000
        if self.vbitrate > vbitrate:
            self.vbitrate = vbitrate
        if float(self.frame_rate) > video['FrameRate']:
            self.frame_rate = str(video['FrameRate'])
        if audio:
            if audio['SamplingRate']:
                sample_rate = audio['SamplingRate'] / 1000
                if self.sample_rate > sample_rate:
                    self.sample_rate = sample_rate
            if audio['BitRate_Maximum'] or audio['BitRate']:
                abitrate = (audio['BitRate_Maximum'] or audio['BitRate']) / 1000
                if self.abitrate > abitrate:
                    self.abitrate = abitrate
            if audio['Channel(s)'] == 1:
                self.channels = 'mono'
        return self