<?php
	// open connection to MySQL server
	$connection = mysql_connect(localhost,$mysqlUser,$mysqlPass)
		or die ('Unable to connect to MySQL!');
	// select database for use
	mysql_select_db($mysqlDatabase) or die ('Unable to select database');
?>