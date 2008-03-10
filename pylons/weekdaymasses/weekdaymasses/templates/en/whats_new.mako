<%inherit file="base.mako" />

%for date in reversed (sorted (c.updates)):
  <p class="whatsnew_date">${h.formatted_date (date)}</p>
  %for text in c.updates[date]:
    <p class="details">${text}</p>
  %endfor
%endfor