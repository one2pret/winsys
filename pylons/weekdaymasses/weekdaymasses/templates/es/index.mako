<%inherit file="base.mako" />

<div id="header">
<p class=details>
Este sitio contiene detalles de las iglesias catolicas y de las
horas de la Misa durante la semana.
</p>
</div>

<table id="content" cellspacing="0">

  <tr>
  
    <td id="worldwide">
      <h2>Worldwide</h2>
      
      <ul>
        <li><a href="$URL$/$LANG$/day/Weekday/area_tree/outside-gb/">Weekday Masses</a> by area sorted by time of day</li>
        <li><a href="$URL$/$LANG$/day/Saturday/area_tree/outside-gb/">Saturday Masses</a> by area sorted by time of day</li>
        <li><a href="$URL$/$LANG$/day/Sunday/area_tree/outside-gb/">Sunday Masses</a> by area sorted by time of day</li>
        <li><a href="$URL$/$LANG$/day/H/area_tree/outside-gb/">Holy Days</a> of Obligation Masses by area sorted by time of day</li>
      </ul>
      
      <ul>
        <li>Masses in airports on <a href="$URL$/$LANG$/day/U/area_tree/airports">Sundays</a> and <a href="$URL$/$LANG$/day/K/area_tree/airports">Weekdays</a></li>
        <li>Masses in holiday areas on <a href="$URL$/$LANG$/day/U/area_tree/holiday-areas">Sundays</a> and <a href="$URL$/$LANG$/day/K/area_tree/holiday-areas">Weekdays</a></li>
      </ul>
    </td>
  
    <td id="gb" rowspan="2">
      <h2>GB</h2>
      
      <ul>
        <li><a href="$URL$/$LANG$/day/Weekday/area_tree/gb/">Weekday Masses</a> by area sorted by time of day</li>
        <li><a href="$URL$/$LANG$/day/Saturday/area_tree/gb/">Saturday Masses</a> by area sorted by time of day</li>
        <li><a href="$URL$/$LANG$/day/Sunday/area_tree/gb/">Sunday Masses</a> by area sorted by time of day</li>
        <li><a href="$URL$/$LANG$/day/H/area_tree/gb/">Holy Days of Obligation Masses</a> by area sorted by time of day</li>
      </ul>
      
      <ul>
        <li>Search for Masses based on <a href="$URL$/$LANG$/postcode/">distance from user-specified GB postcode area</a></li>
        <li>Search for Masses near <a href="$URL$/$LANG$/motorway/">motorway junctions</a></li>
        <li><a href="$URL$/$LANG$/shrine/">View list</a> of churches or shrines dedicated to our Lady by general area</li>
        <li>View the <a href="$URL$/$LANG$/day/K/area/gb/churches">entire GB list of churches</a></li>
      </ul>
    
    </td>
  
  </tr>

  <tr><td id="search">
    <h2>Search</h2>
    <ul>
    <li>Find a church by name or area:
      <form class="search" action="$URL$/$LANG$/search" method="GET">
        <input class="text-box" type="text" name="terms" />
        <input class="go-button" type="submit" value="Find">
      </form>
    </li>
    </ul>
  </td></tr>

  <tr><td id="general" colspan="2">
    <h2>General</h2>
    
    <ul>
      <li>View <a href="$URL$/$LANG$/links">links</a> to helpful reading material on the Holy Sacrifice of the Mass</li>
      <li>For any corrections, questions or updates, please contact the <a href="$URL$/$LANG$/contact">Site Administrator</a></li>
      <li>Last updated $LAST_UPDATE$. See <a href="$URL$/$LANG$/whats_new">What's New?</a></li>
    </ul>
  </td></tr>

</table>

<div id="footer">

<p class="details">
This site relies on you to provide corrections, additions and updates.
If there's a church you know about, give us the details and we'll add them in.
If you find that the times have changed, let us know and we'll update the information.
While we try to keep the information up to date, it's worth ringing to make sure if you're
going out of your way.
</p>

</div>
