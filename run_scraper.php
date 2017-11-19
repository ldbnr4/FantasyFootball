<?php
    $output = shell_exec('python main.py');
    if ($output == NULL){
        echo "<pre>ERROR</pre>";
    }
    else
        echo "<pre>$output</pre>";
?>