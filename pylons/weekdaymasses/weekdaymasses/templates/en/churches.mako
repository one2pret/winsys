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
  
  % if church.address or church.map_links ():
    <p class="address">
  % endif
  
  % if church.map_links ():
    ${" - ".join ('<a class="map_link" href="%s">%s</a>' % (url, text) for (url, text) in church.map_links ())}
    <br />
  % endif

% endfor