from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
_magic_number = 2
_modified_time = 1205061667.875
_template_filename=u'C:\\temp\\pylons\\weekdaymasses\\weekdaymasses\\templates/es/index.mako'
_template_uri=u'/es/index.mako'
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
        # SOURCE LINE 1
        context.write(u'\n\n<div id="header">\n<p class=details>\nEste sitio contiene detalles de las iglesias catolicas y de las\nhoras de la Misa durante la semana.\n</p>\n</div>\n\n<table id="content" cellspacing="0">\n\n  <tr>\n  \n    <td id="worldwide">\n      <h2>Worldwide</h2>\n      \n      <ul>\n        <li><a href="$URL$/$LANG$/day/Weekday/area_tree/outside-gb/">Weekday Masses</a> by area sorted by time of day</li>\n        <li><a href="$URL$/$LANG$/day/Saturday/area_tree/outside-gb/">Saturday Masses</a> by area sorted by time of day</li>\n        <li><a href="$URL$/$LANG$/day/Sunday/area_tree/outside-gb/">Sunday Masses</a> by area sorted by time of day</li>\n        <li><a href="$URL$/$LANG$/day/H/area_tree/outside-gb/">Holy Days</a> of Obligation Masses by area sorted by time of day</li>\n      </ul>\n      \n      <ul>\n        <li>Masses in airports on <a href="$URL$/$LANG$/day/U/area_tree/airports">Sundays</a> and <a href="$URL$/$LANG$/day/K/area_tree/airports">Weekdays</a></li>\n        <li>Masses in holiday areas on <a href="$URL$/$LANG$/day/U/area_tree/holiday-areas">Sundays</a> and <a href="$URL$/$LANG$/day/K/area_tree/holiday-areas">Weekdays</a></li>\n      </ul>\n    </td>\n  \n    <td id="gb" rowspan="2">\n      <h2>GB</h2>\n      \n      <ul>\n        <li><a href="$URL$/$LANG$/day/Weekday/area_tree/gb/">Weekday Masses</a> by area sorted by time of day</li>\n        <li><a href="$URL$/$LANG$/day/Saturday/area_tree/gb/">Saturday Masses</a> by area sorted by time of day</li>\n        <li><a href="$URL$/$LANG$/day/Sunday/area_tree/gb/">Sunday Masses</a> by area sorted by time of day</li>\n        <li><a href="$URL$/$LANG$/day/H/area_tree/gb/">Holy Days of Obligation Masses</a> by area sorted by time of day</li>\n      </ul>\n      \n      <ul>\n        <li>Search for Masses based on <a href="$URL$/$LANG$/postcode/">distance from user-specified GB postcode area</a></li>\n        <li>Search for Masses near <a href="$URL$/$LANG$/motorway/">motorway junctions</a></li>\n        <li><a href="$URL$/$LANG$/shrine/">View list</a> of churches or shrines dedicated to our Lady by general area</li>\n        <li>View the <a href="$URL$/$LANG$/day/K/area/gb/churches">entire GB list of churches</a></li>\n      </ul>\n    \n    </td>\n  \n  </tr>\n\n  <tr><td id="search">\n    <h2>Search</h2>\n    <ul>\n    <li>Find a church by name or area:\n      <form class="search" action="$URL$/$LANG$/search" method="GET">\n        <input class="text-box" type="text" name="terms" />\n        <input class="go-button" type="submit" value="Find">\n      </form>\n    </li>\n    </ul>\n  </td></tr>\n\n  <tr><td id="general" colspan="2">\n    <h2>General</h2>\n    \n    <ul>\n      <li>View <a href="$URL$/$LANG$/links">links</a> to helpful reading material on the Holy Sacrifice of the Mass</li>\n      <li>For any corrections, questions or updates, please contact the <a href="$URL$/$LANG$/contact">Site Administrator</a></li>\n      <li>Last updated $LAST_UPDATE$. See <a href="$URL$/$LANG$/whats_new">What\'s New?</a></li>\n    </ul>\n  </td></tr>\n\n</table>\n\n<div id="footer">\n\n<p class="details">\nThis site relies on you to provide corrections, additions and updates.\nIf there\'s a church you know about, give us the details and we\'ll add them in.\nIf you find that the times have changed, let us know and we\'ll update the information.\nWhile we try to keep the information up to date, it\'s worth ringing to make sure if you\'re\ngoing out of your way.\n</p>\n\n</div>\n')
        return ''
    finally:
        context.caller_stack.pop_frame()


