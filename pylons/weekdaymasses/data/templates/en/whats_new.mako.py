from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
_magic_number = 2
_modified_time = 1205100336.03
_template_filename=u'C:\\temp\\pylons\\weekdaymasses\\weekdaymasses\\templates/en/whats_new.mako'
_template_uri=u'/en/whats_new.mako'
_template_cache=cache.Cache(__name__, _modified_time)
_source_encoding=None
_exports = []


def _mako_get_namespace(context, name):
    try:
        return context.namespaces[(__name__, name)]
    except KeyError:
        _mako_generate_namespaces(context)
        return context.namespaces[(__name__, name)]
def _mako_generate_namespaces(context):
    pass
def _mako_inherit(template, context):
    _mako_generate_namespaces(context)
    return runtime._inherit_from(context, u'base.mako', _template_uri)
def render_body(context,**pageargs):
    context.caller_stack.push_frame()
    try:
        __M_locals = dict(pageargs=pageargs)
        h = context.get('h', UNDEFINED)
        c = context.get('c', UNDEFINED)
        # SOURCE LINE 1
        context.write(u'\n\n')
        # SOURCE LINE 3
        for date in reversed (sorted (c.updates)):
            # SOURCE LINE 4
            context.write(u'  <p class="whatsnew_date">')
            context.write(unicode(h.formatted_date (date)))
            context.write(u'</p>\n')
            # SOURCE LINE 5
            for text in c.updates[date]:
                # SOURCE LINE 6
                context.write(u'    <p class="details">')
                context.write(unicode(text))
                context.write(u'</p>\n')
        return ''
    finally:
        context.caller_stack.pop_frame()


