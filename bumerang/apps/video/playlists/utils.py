# -*- coding: utf-8 -*-
from datetime import date

from django.utils.timezone import now, localtime


class PlayListMixin(object):
    def __init__(self, channel, when=None):
        self.when = when or date.today()
        self.channel = channel
        self.playlist = self.get_playlist()

    def get_playlist(self):
        last = list(self.channel.playlist_set.filter(
            rotate_from_date__lte=self.when).order_by('-rotate_from_date')[:1])
        if last:
            playlist = last[0]
            playlist.rotate_from_date = self.when
            return playlist
        return None


class CurrentItem(PlayListMixin):
    current_block = None
    current_item = None

    def __init__(self, *args, **kwargs):
        super(CurrentItem, self).__init__(*args, **kwargs)
        self.offset = self.get_offset()
        self.offset_in_cycle = self.get_offset_in_cycle()
        self.current_block = self.get_current_block()
        if self.current_block:
            self.offset_in_block = self.get_offset_in_block()
            self.current_item = self.get_current_item()
        self.countdown = self.get_countdown()

    def get_offset(self):
        """ offset of now from playlist start time in seconds"""
        n = localtime(now())
        return n.hour * 3600 + n.minute * 60 + n.second

    def get_offset_in_cycle(self):
        """ in seconds """
        return self.offset % (self.playlist.duration * 3600)

    def get_current_block(self):
        for block in self.playlist.playlistblock_set.all():
            if (0 < self.offset_in_cycle - block.block_offset() * 60
                    < block.limit * 60):
                return block
        return None

    def get_offset_in_block(self):
        """offset in seconds"""
        return self.offset_in_cycle - self.current_block.block_offset() * 60

    def get_current_item(self):
        if self.current_block:
            return self.current_block.playlistitem_set.filter(
                offset__lt=self.offset_in_block * 1000).latest('offset')
        return None

    def get_countdown(self):
        # countdown until next cycle
        cds = [self.playlist.duration * 3600 - self.get_offset_in_cycle()]
        if self.current_block:
            # countdown until next block
            cds.append(self.current_block.limit * 60 - self.offset_in_block)
        if self.current_item:
            item = self.current_item
            # countdown until next item
            cds.append((item.offset + item.video.duration)
                       / 1000 - self.offset_in_block)
        # return the least of countdowns
        return sorted(cds)[0]

    def get_current_cycle(self):
        return self.offset / self.playlist.duration * 3600


class Schedule(PlayListMixin):
    def items(self):
        for block in self.playlist.blocks():
            for item in block.playlistitem_set.all():
                yield item
