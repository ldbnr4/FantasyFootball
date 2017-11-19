<?php
    header('Access-Control-Allow-Origin: *');
    $output = shell_exec('python main.py');
    if ($output == NULL){
        echo "<pre>ERROR</pre>";
    }
    else
        echo "<pre>$output</pre>";
?>