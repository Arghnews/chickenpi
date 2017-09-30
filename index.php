<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Chickenpi</title>
<style>
    body {
        width: 35em;
        margin: 0 auto;
        font-family: Tahoma, Verdana, Arial, sans-serif;
    }
</style>

<script src=jquery-3.2.1.js>
</script>

</head>

<body>

<h1>Welcome to the chickenpi controller!</h1>
<p>If you see this page, the nginx web server is successfully installed and
working on Debian. Further configuration is required.</p>

<p>For online documentation and support please refer to
<a href="http://nginx.org/">nginx.org</a></p>

<p>
      Please use the <tt>reportbug</tt> tool to report bugs in the
      nginx package with Debian. However, check <a
      href="http://bugs.debian.org/cgi-bin/pkgreport.cgi?ordering=normal;archive=0;src=nginx;repeatmerged=0">existing
      bug reports</a> before reporting a new bug.
</p>

<p><em>Thank you for using debian and nginx.</em></p>

<p>This is another paragraph.</p>

<!--<button class=door> near door - open </button> -->

<div id=doors>
    Loading doors data...
</div>

<br>
<br>
<?php
    function br() {
        echo "<br>";
    }
    echo "Hi from php -> unix time ".time()."";
    br();
    $localname = `hostname`;
    $ip = `hostname -I`;
    $my_location = `pwd`;
    echo "My name is $localname and I'm at $ip";
    br();
    echo "I'm stored in $my_location";
    br();


    $old_path = getcwd();
    echo "$old_path";
    br();
    chdir('/var/www/html/scripts');
    $p = `./echo.py`;
    chdir($old_path);

    echo "p returned $p";
    br();
?>

<script>
$(document).ready(function(){

        var data_to_send = {}
        data_to_send["request"] = "list_doors"
        console.log("Asking for doors list")
        var serialized = JSON.stringify(data_to_send)
        console.log("Sending",serialized)

        $.post("door_action.php", serialized, function(json_data, textStatus, jqXHR) {
            console.log("Returned with code:", textStatus, jqXHR)
            console.log("Returned with data:", json_data)
            //var data = JSON.parse(json_data)
            var reply = json_data
            console.log(reply)
            console.log(reply["response"])

            var doors_html = ""
            var doors_info = reply["response"]

            for (var i=0; i<doors_info.length; ++i) {
                var html = ""
                var door = doors_info[i]
                var door_name = door["door_name"]
                var door_actions = door["door_actions"]

                console.log("Door:",door_name)
                console.log(door_actions)

                html += "<br><div data-door_name=" + door_name + ">"
                html += door_name
                html += "<span class=status></span><br>"

                for (var j=0; j<door_actions.length; ++j) {
                    var door_action = door_actions[j]
                    html += "<button"
                    html += " name=" + door_name
                    html += " class=\"" + "door_button " + door_action
                    html += "\">"
                    html += door_action
                    html += "</button>"
                    html += " "
                }

                html += "</div>"
                doors_html += html
            }
            $("div#doors").replaceWith(doors_html)
            
        }, "json")

    // door buttons
    // on binds to new eles
    $(document).on("click",".door_button", function(){

        var me = $(this)

        console.log(me)
        //console.log(me[0].outerHTML)
        var door_name = me.attr("name")
        var action = me.attr("class") // open, close, stop

        var data_to_send = {}
        data_to_send["request"] = "door_action"
        data_to_send["door_name"] = door_name
        data_to_send["door_action"] = action

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

</body>
</html>
