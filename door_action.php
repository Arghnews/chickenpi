<?php

//error_report(E_ALL);
//ini_set("display_errors", 1);

// just passes data (in json) to python script that returns data as json
// currently don't need json encode stuff as just passes

// in
$json = file_get_contents('php://input');
//$data_in = json_decode($json,TRUE);

$reply = "";

$fp = fsockopen("localhost", 2520, $errno, $errstr, 5);
if (!$fp) {
    echo "$errstr ($errno)<br />\n";
} else {
    // write out json string to socket
    fwrite($fp, $json);
    if (!feof($fp)) {
        // read reply until newline
        $reply = fgets($fp);
    }
    fclose($fp);
}

// out
$data = $reply;
//echo json_encode($data);
echo $data;

?>
