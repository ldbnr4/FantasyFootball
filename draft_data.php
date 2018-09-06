<?php
    header('Access-Control-Allow-Origin: *');
    // $output = shell_exec('python main.py -s');
    $output = file_get_contents('season.json');
    if ($output == NULL){
        echo "ERROR";
    }
    else
        echo $output;
?>