from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
_magic_number = 2
_modified_time = 1205093914.483
_template_filename=u'C:\\temp\\pylons\\weekdaymasses\\weekdaymasses\\templates/en/whatsnew.mako'
_template_uri=u'/en/whatsnew.mako'
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
        c = context.get('c', UNDEFINED)
        utils = context.get('utils', UNDEFINED)
        # SOURCE LINE 1
        context.write(u'\n\n')
        # SOURCE LINE 3
        for date in c.updates.keys ():
            # SOURCE LINE 4
            context.write(u'<h2>')
            context.write(unicode(utils.formatted_date (date)))
            context.write(u'</h2>\n')
        return ''
    finally:
        context.caller_stack.pop_frame()


