from django.contrib.sites.models import Site
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django.core.cache import cache

from .settings import CACHE_PREFIX


@python_2_unicode_compatible
class FlatBlock(models.Model):
    """
    Think of a flatblock as a flatpage but for just part of a site. It's
    basically a piece of content with a given name (slug) and an optional
    title (header) which you can, for example, use in a sidebar of a website.
    """
    site = models.ForeignKey(Site)
    slug = models.CharField(max_length=255,
                            verbose_name=_('Slug'),
                            help_text=_("A unique name used for reference in "
                                        "the templates"))
    header = models.CharField(blank=True, null=True, max_length=255,
                              verbose_name=_('Header'),
                              help_text=_("An optional header for this "
                                          "content"))
    content = models.TextField(verbose_name=_('Content'), blank=True,
                               null=True)

    # Helper attributes used if content should be evaluated in order to
    # represent the original content.
    raw_content = None
    raw_header = None

    def __str__(self):
        return self.slug

    def save(self, *args, **kwargs):
        super(FlatBlock, self).save(*args, **kwargs)
        # Now also invalidate the cache used in the templatetag
        cache.delete('%s%s_%s' % (CACHE_PREFIX, self.site_id, self.slug, ))

    def delete(self, *args, **kwargs):
        cache_key = '%s%s_%s' % (CACHE_PREFIX, self.site_id, self.slug,)
        super(FlatBlock, self).delete(*args, **kwargs)
        cache.delete(cache_key)

    class Meta:
        verbose_name = _('Flat block')
        verbose_name_plural = _('Flat blocks')
        unique_together = ('site', 'slug')
