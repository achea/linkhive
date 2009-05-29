<?php
	include 'config.php';
	include 'opendb.php';
	require_once("functions.php");
	require_once("paginator.class.php");

?>
<!DOCTYPE html
PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html>
	<head>
		<title>dStory Viewer</title>
		<link rel="stylesheet" type="text/css" href="dstory.css" media="screen" />
		<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
	</head>
	<body>
		<div id="wrapper">
			<div class="main">


<?php
	//$search="WHERE (MATCH(title,description) AGAINST ('school education parent grade' IN BOOLEAN MODE))";
	//$search="WHERE (MATCH(title,description) AGAINST ('theory' IN BOOLEAN MODE))";
	$search="";

	// get rows
	$num_rows = getNumRows($search);

	$pages	= new Paginator();
	$pages->items_total = $num_rows;
	$pages->mid_range = 9;
	echo "<div class=\"paginate\">";
	$pages->paginate();
	echo $pages->display_pages();

	echo "<span style=\"margin-left:25px\"> ". $pages->display_jump_menu() . $pages->display_items_per_page() . "</span>";

	echo "</div>\n";

	// print the stories

	printStoriesPaginator($pages,$search);

	echo "<div class=\"paginate\">" . $pages->display_pages() . "</div>";
	echo "<p>Page $pages->current_page of $pages->num_pages </p>";  

	include 'closedb.php';

?>

		</div></div>

	</body>
</html>
