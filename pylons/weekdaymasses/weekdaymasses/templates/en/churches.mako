<%inherit file="base.mako" />

% for church in c.churches:

  <h3 id="p${church.id}" 
  % if church.id == c.church_id:
    class="highlight"
  % endif
  >
  ${church.full_name}</h3>

  % for day_code in [u'K', u'U', u'A', u'H']:
    <% 
      day = c.model.Day.get_by (code=day_code)
      mass_times = church.daily_mass_times (day_code)
    %>
    % if mass_times:
      <p class="times">${day.name}: ${mass_times}</p>
    % endif
  % endfor
  
  % if church.address or church.x_coord or church.latitude or church.map_link:
    <p class="address">
  % endif
  
<%
  if church.map_link:
    map_link = u"http://%s" % church.map_link
  if church.x_coord and church.y_coord:
    streetmap_link = u"http://www.streetmap.co.uk/streetmap.dll?g2m?X=%d&Y=%d&a=Y&z=%d" % (church.x_coord, church.y_coord, church.zoom_level)
  if church.latitude and church.longitude and church.scale:
    latitude = float (church.latitude)
    longitude = float (church.longitude)
    scale = float (church.scale)
    multimap_link = u"http://www.multimap.com/map/browse.cgi?lat=%6.4f&lon=%6.4f&scale=%d&icon=x&mapsize=big" % (latitude, longitude, scale)
    gmap_link = u"http://maps.google.com?f=q&q=%s,%s&ll=%s,%s&ie=utf8&z=16&iwloc=addr&om=1" % (latitude, longitude, latitude, longitude)
    
  
    map_links.append (u'[<a href="http://%(map_link)s" class="map_link">Map link</a>]' % church)

  if church.x_coord and church.y_coord:
    map_href = u"http://www.streetmap.co.uk/streetmap.dll?g2m?X=%(x_coord)d&Y=%(y_coord)d&a=Y&z=%(zoom_level)d" % church
    map_links.append (u'[<a href="%s" class="map_link">Streetmap link</a>]' % map_href)

  if church.latitude and church.longitude and church.scale:
    latitude = float (church.latitude)
    longitude = float (church.longitude)
    scale = float (church.scale)
    map_href = u"http://www.multimap.com/map/browse.cgi?lat=%6.4f&lon=%6.4f&scale=%d&icon=x&mapsize=big" % (latitude, longitude, scale)
    map_links.append (u'[<a href="%s" class="map_link">Multimap link</a>]' % map_href)
    
    gmap_href = u"http://maps.google.com?f=q&q=%(latitude)s,%(longitude)s&ll=%(latitude)s,%(longitude)s&ie=utf8&z=16&iwloc=addr&om=1" % church
    map_links.append (u'[<a href="%s" class="map_link">Google Maps</a>]' % gmap_href)

  if map_links:
    html.append (u" - ".join (map_links))
    html.append (u"<br />")
%>


% endfor