<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <!-- meta name="verify-v1" content="P6x5UZUvbcpZ9CBG4lsI/99vbk0yTe8T/ar3Jka+Grc=" / -->
    ${h.stylesheet_link_tag ("/css/weekdaymasses.css")}
    %for area in c.areas:
      ${h.stylesheet_link_tag ("/css/%s.css") % area}
    %endfor
    <title>${c.title}</title>
  </head>
    <!-- script src="http://www.google-analytics.com/urchin.js" type="text/javascript"></script>
    <script type="text/javascript">
    _uacct = "UA-2798383-2";
    urchinTracker();
    </script -->
  <body>
  
    <div id="header">
      ${self.header ()}
    </div>

    ${self.quick_links ()}
    <div class="body">
      <h1>${c.title}</h1>
      ${self.body ()}
    </div>
    ${self.quick_links ()}
    
    <div id="footer">
      ${self.footer ()}
    </div>
  
  </body>
</html>

<%def name="header ()">
</%def>

<%def name="footer ()">
</%def>
