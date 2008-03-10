from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
_magic_number = 2
_modified_time = 1205062174.3429999
_template_filename=u'C:\\temp\\pylons\\weekdaymasses\\weekdaymasses\\templates/en/base.mako'
_template_uri=u'/en/base.mako'
_template_cache=cache.Cache(__name__, _modified_time)
_source_encoding=None
_exports = ['quick_links']


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
    return runtime._inherit_from(context, u'/base.mako', _template_uri)
def render_body(context,**pageargs):
    context.caller_stack.push_frame()
    try:
        __M_locals = dict(pageargs=pageargs)
        # SOURCE LINE 1
        context.write(u'\n\n')
        # SOURCE LINE 14
        context.write(u'\n')
        return ''
    finally:
        context.caller_stack.pop_frame()


def render_quick_links(context):
    context.caller_stack.push_frame()
    try:
        c = context.get('c', UNDEFINED)
        # SOURCE LINE 3
        context.write(u'\n  <div class="links">\n    <a href="/')
        # SOURCE LINE 5
        context.write(unicode(c.language))
        context.write(u'/" class="internal">[Home]</a>\n    <a href="/')
        # SOURCE LINE 6
        context.write(unicode(c.language))
        context.write(u'/area/gb/postcodes/" class="internal">[GB Churches by Postcode]</a>\n    <a href="/')
        # SOURCE LINE 7
        context.write(unicode(c.language))
        context.write(u'/day/Weekday/area_tree/gb/" class="internal">[GB Weekday Masses by Area]</a>\n    <a href="/')
        # SOURCE LINE 8
        context.write(unicode(c.language))
        context.write(u'/area/gb/churches" class="internal">[All GB Churches]</a>\n    <a href="/')
        # SOURCE LINE 9
        context.write(unicode(c.language))
        context.write(u'/shrine/" class="internal">[Shrines]</a>\n    <a href="/')
        # SOURCE LINE 10
        context.write(unicode(c.language))
        context.write(u'/whats_new/" class="internal">[What\'s New?]</a>\n    <a href="/')
        # SOURCE LINE 11
        context.write(unicode(c.language))
        context.write(u'/links/" class="internal">[Links]</a>\n    <a href="/')
        # SOURCE LINE 12
        context.write(unicode(c.language))
        context.write(u'/search/" class="internal">[Find]</a>\n  </div>\n')
        return ''
    finally:
        context.caller_stack.pop_frame()


