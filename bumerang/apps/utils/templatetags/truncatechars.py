# -*- coding: utf-8 -*-
from django import template
register = template.Library()

@register.filter
def truncatechars(value, max_length):
#    """
#    Truncates a word after a given number of chars
#    Argument: Number of chars to truncate after
#    """
#    length = int(num)
#    string = []
#    for word in s.split():
#        if len(word) > length:
#            string.append(word[:length]+'...')
#        else:
#            string.append(word)
#    return u' '.join(string)

    if len(value) > max_length:
        truncd_val = value[:max_length]
        if not len(value) == max_length+1 and value[max_length+1] != " ":
            truncd_val = truncd_val[:truncd_val.rfind(" ")]
        return  truncd_val + "..."
    return value