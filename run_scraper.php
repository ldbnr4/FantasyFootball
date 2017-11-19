<?php
    header('Access-Control-Allow-Origin: *');
    $output = shell_exec('python main.py');
    if ($output == NULL){
        echo "ERROR";
    }
    else
        echo $output;
?>