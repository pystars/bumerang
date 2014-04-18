# -*- coding: utf-8 -*-

def paginator_context(request):
    if request.GET:
        query = request.GET.copy()
        if 'page' in query:
            del query['page']
        return {'query_string':
                    '&' + '&'.join(k + '=' + query[k] for k in query)}
    return {}
