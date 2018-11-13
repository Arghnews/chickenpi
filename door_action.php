<?php

/*
 * Forwards string input from stdin to open socket on localhost
 * that is assumed to be receiving in (python) program.
 * Reads reply until $response_end_string then echoes it.
 * Not exception safe
 * If response doesn't have $response_end_string may read forever or
 * at least until eof
 */

$response_end_string = "END_OF_MESSAGE\n";

$message = file_get_contents('php://input');

$response = "";

$fp = fsockopen("localhost", 2520, $errno, $errstr, 5);
if (!$fp) {
    $response = "$errstr ($errno)<br />\n";
} else {
    fwrite($fp, $message);
    if (!feof($fp)) {
        $response = file_get_contents($response_end_string);
    }
    fclose($fp);
}

echo $response;

?>
