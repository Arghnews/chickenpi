<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Chickenpi</title>
<style>
    body {
        width: 25em;
        margin: 0 auto;
        font-family: Tahoma, Verdana, Arial, sans-serif;
    }
    button {
        width: 10em; height: 4em; margin: 0.8em; font-weight: bold;
    }

</style>

<script src=jquery-3.2.1.js>
</script>

</head>

<body>

<h4>Welcome to the chickenpi controller!</h4>
<!--<button class=door> near door - open </button> -->

<div id=doors>
    Loading doors data...
</div>

<?php
    function br() {
        echo "<br>";
    }
?>

<script>
$(document).ready(function(){

    // TODO: this shit is such a fucking mess and I hate it enough to learn
    // some react and rewrite it. Do this.

    (function () {

    var clockElement = document.getElementById( "clock" );

    function updateClock ( clock ) {
        var event = new Date();
        utc_string = event.toLocaleString('en-GB', { timeZone: 'Etc/UTC' });
        local_string = event.toLocaleString('en-GB', { timeZone: 'Europe/London' });
        clock.innerHTML = "Time now (UTC): " + utc_string +
                    "<br>Time now (local): " + local_string;
      }

    updateClock(clockElement);
      setInterval(function () {
          updateClock( clockElement );
      }, 5000);

    }());

    var data_to_send = {}
    data_to_send["request"] = "list_doors"
    console.log("Asking for doors list")
    var serialized = JSON.stringify(data_to_send)
    console.log("Sending",serialized)
    console.log("Sending",serialized)

    $.post("door_action.php", serialized, function(json_data, textStatus, jqXHR) {
        console.log("Returned with code:", textStatus, jqXHR)
        console.log("Returned with data:", json_data)
        //var data = JSON.parse(json_data)
        var reply = json_data

        console.log("Response key:", reply["response"])

        var doors_html = ""
        var response = reply["response"]
        var doors_info = response["doors"]

        for (var i=0; i<doors_info.length; ++i) {
            var html = ""
            var door = doors_info[i]
            var door_name = door["door_name"]
            var door_actions = door["door_actions"]

            console.log("Door:",door_name)
            console.log(door_actions)

            html += "<div data-door_name=\"" + door_name + "\">"
            html += door_name
            html += "<span class=status></span><br>"

            for (var j=0; j<door_actions.length; ++j) {
                var door_action = door_actions[j]
                html += "<button"

                html += " name=\"" + door_name + "\""
                html += " class=\"door_button\""
                html += " data-action=\"" + door_action + "\""

                html += ">" + door_action
                html += "</button> "
            }

            html += "</div>"
            doors_html += html
        }

        console.log("-----")
        $("div#doors").replaceWith(doors_html)

		/* var event = new Date(); */
		/* var event = new Date(); */

		// British English uses day-month-year order and 24-hour time without AM/PM
		/* https://en.wikipedia.org/wiki/List_of_tz_database_time_zones */
		/* console.log(event.toLocaleString('en-GB', { timeZone: 'Etc/UTC' })); */
		/* console.log(event.toLocaleString('en-GB', { timeZone: 'Europe/London' })); */
		/* console.log("") */

        /* closing_html = "<br><br>Coop door opening and closing times" */
        closing_html = "<br><i>(Scroll the page down!)</i><br>";
        closing_html += "<ul>";
	    closing_html += "<li>Coop doors open and close at <b>earliest open and latest close</b> times</li>"
	    closing_html += "<li>Refresh this page to see updated information</li>"
	    closing_html += "<li>Sunset/sunrise and open/close times change daily</li>"
        closing_html += "</ul>";
        /* closing_html += "<br>Coop will close at sunset (note timezones)"; */
        /* closing_html += "<br>Sunrise time (UTC): " + response["sunrise"] */
        /* closing_html += "<br>Sunset time (UTC): " + response["sunset"] */
	    closing_html += response["times_today_str"]
        $("div#sun_times").replaceWith(closing_html)

        /* console.log("My") */
        console.log("Responded with sunrise:", response["sunrise"])
        /* console.log("sharona") */
        console.log("Responded with sunset:", response["sunset"])

    }, "json")

    // door buttons
    // on binds to new eles
    $(document).on("click",".door_button", function(){

        var me = $(this)

        console.log(me)
        //console.log(me[0].outerHTML)
        var door_name = me.attr("name")
        var action = me.attr("data-action") // open, close, stop

        var data_to_send = {}
        data_to_send["request"] = "door_action"
        data_to_send["door_name"] = door_name
        data_to_send["door_action"] = action

        if (action === "open")
        {
            var msg = "WARNING: are you SURE you want to open that door?";
            msg += "(Think of chicken safety!)";
            if (confirm(msg))
            {
                console.log("Change made");
            }
            else
            {
                console.log("Nothing changed - user opted out of confirm");
                return;
            }
        }

        console.log("Data to send",data_to_send)
        var serialized = JSON.stringify(data_to_send);
        console.log("Sending",serialized)

        $.post("door_action.php", serialized, function(json_data, textStatus, jqXHR) {
            console.log("Returned with code:", textStatus, jqXHR)
            console.log("Returned with data:", json_data)
            //var data = JSON.parse(json_data)
            var data = json_data

            var reply = json_data
            console.log(reply)
            console.log(reply["response"])

            var doors_html = ""
            var doors_info = reply["response"]
            var status = reply["status"]
            console.log(status)
            var status_span = me.parent("div").find("span.status")
            status_span.html(" - status:" + status)

        }, "Json")
    });
});
</script>

<br>

<div id=clock>
</div>
<div id=sun_times>
</div>
<div id=current_door_times>
</div>

</body>
</html>
