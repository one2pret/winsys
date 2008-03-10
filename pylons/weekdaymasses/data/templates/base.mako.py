from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
_magic_number = 2
_modified_time = 1205094284.951
_template_filename=u'C:\\temp\\pylons\\weekdaymasses\\weekdaymasses\\templates/base.mako'
_template_uri=u'/base.mako'
_template_cache=cache.Cache(__name__, _modified_time)
_source_encoding=None
_exports = ['header', 'footer']


def render_body(context,**pageargs):
    context.caller_stack.push_frame()
    try:
        __M_locals = dict(pageargs=pageargs)
        h = context.get('h', UNDEFINED)
        c = context.get('c', UNDEFINED)
        self = context.get('self', UNDEFINED)
        # SOURCE LINE 1
        context.write(u'<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">\n<html>\n  <head>\n    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">\n    <!-- meta name="verify-v1" content="P6x5UZUvbcpZ9CBG4lsI/99vbk0yTe8T/ar3Jka+Grc=" / -->\n    ')
        # SOURCE LINE 6
        context.write(unicode(h.stylesheet_link_tag ("/css/weekdaymasses.css")))
        context.write(u'\n')
        # SOURCE LINE 7
        for area in c.areas:
            # SOURCE LINE 8
            context.write(u'      ')
            context.write(unicode(h.stylesheet_link_tag ("/css/%s.css") % area))
            context.write(u'\n')
        # SOURCE LINE 10
        context.write(u'    <title>')
        context.write(unicode(c.title))
        context.write(u'</title>\n  </head>\n    <!-- script src="http://www.google-analytics.com/urchin.js" type="text/javascript"></script>\n    <script type="text/javascript">\n    _uacct = "UA-2798383-2";\n    urchinTracker();\n    </script -->\n  <body>\n  \n    <div id="header">\n      ')
        # SOURCE LINE 20
        context.write(unicode(self.header ()))
        context.write(u'\n    </div>\n\n    ')
        # SOURCE LINE 23
        context.write(unicode(self.quick_links ()))
        context.write(u'\n    <div class="body">\n      <h1>')
        # SOURCE LINE 25
        context.write(unicode(c.title))
        context.write(u'</h1>\n      ')
        # SOURCE LINE 26
        context.write(unicode(self.body ()))
        context.write(u'\n    </div>\n    ')
        # SOURCE LINE 28
        context.write(unicode(self.quick_links ()))
        context.write(u'\n    \n    <div id="footer">\n      ')
        # SOURCE LINE 31
        context.write(unicode(self.footer ()))
        context.write(u'\n    </div>\n  \n  </body>\n</html>\n\n')
        # SOURCE LINE 38
        context.write(u'\n\n')
        # SOURCE LINE 41
        context.write(u'\n')
        return ''
    finally:
        context.caller_stack.pop_frame()


def render_header(context):
    context.caller_stack.push_frame()
    try:
        # SOURCE LINE 37
        context.write(u'\n')
        return ''
    finally:
        context.caller_stack.pop_frame()


def render_footer(context):
    context.caller_stack.push_frame()
    try:
        # SOURCE LINE 40
        context.write(u'\n')
        return ''
    finally:
        context.caller_stack.pop_frame()


