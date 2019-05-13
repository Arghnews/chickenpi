<?php

/* https://stackoverflow.com/a/541463 */
/* For function to get all headers */

/* https://www.php.net/manual/en/function.pack.php
/* stanislav dot eckert at vizson dot de */

function int_to_unsigned_4byte_big_endian($i)
{
    return pack("N", $i);
}

error_reporting(E_ALL);

$message = file_get_contents('php://input');

$content_length_header = $_SERVER['HTTP_CONTENT_LENGTH'];
$content_length_int = intval($content_length_header);
$content_length_bytes = int_to_unsigned_4byte_big_endian($content_length_int);
/* echo "CONTENT_LENGTH_HEADER:".$content_length_header; */
/* echo "CONTENT_LENGTH_INT:".$content_length_int; */
/* echo "CONTENT_LENGTH_BYTES:".$content_length_bytes; */

$fp = fsockopen("127.0.0.1", 2520, $errno, $errstr, 5);
if (!$fp) {
    echo "{\"error\": \"$errstr ($errno)\"}";
} else {
    fwrite($fp, $content_length_bytes.$message);
    $response = "";
    while (!feof($fp))
    {
        $response .= stream_get_contents($fp);
    }
    echo $response;
    fclose($fp);
}

/* foreach ($headers as $header => $value) { */
/*     echo "$header: $value <br />\n"; */
/* } */

/* $content_length = intval($headers["Content-Length"]); */

/* echo "Content length: $content_length"; */

/* $test_string = <<<TEST_STRING */
/* { */
/*   "response": [ */
/*     { */
/*       "door_name": "door1", */
/*       "door_actions": [ */
/*         "a1", */
/*         "a2", */
/*         $response */
/*       ] */
/*     } */
/*   ] */
/* } */
/* TEST_STRING; */

/*  echo $test_string; */
