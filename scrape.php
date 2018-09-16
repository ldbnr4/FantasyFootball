<?php
    header('Access-Control-Allow-Origin: *');
    $output = file_get_contents('scrape.json');
    if ($output == NULL){
        echo "ERROR";
    }
    else
        echo $output;
?>
