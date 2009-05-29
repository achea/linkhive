<?php

	//This file has some auxilliary functions for general usage ^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,6}$

	function getNumRows($addquery)
	{	// how many rows we have in database
		$query   = "SELECT COUNT(id) AS numrows FROM story_data " . $addquery;
		$result  = mysql_query($query) or die('Error, query failed');
		$row     = mysql_fetch_array($result, MYSQL_ASSOC);
		$numrows = $row['numrows'];

		return $numrows;
	}

	function showDate ($status, $submit_date, $promote_date)
	{
		$date;
		if (!strcmp($status, "popular"))
		{
			echo "made popular ";
			$date = $promote_date;
		} elseif (!strcmp($status, "upcoming"))
		{
			echo "submitted ";
			$date = $submit_date;
		}

		//"2008-04-03 15:14:54"
		echo "<span class=\"d\" property=\"dc:date\" content=\"" . date("Y-m-d H:m:s", $date) . "\"> <span class=\"d\">" . diffDate($date, time()) .  " ago</span></span>";
	}

	function diffDate($start, $end)
	{
		//assume $start is lower

		$dateDiff = $end - $start;		//in seconds

		$fullYears = floor($dateDiff/(60*60*24*365.25));
		$fullDays = floor($dateDiff/(60*60*24));
		$fullHours = floor(($dateDiff-($fullDays*60*60*24))/(60*60));
		$fullMinutes = floor(($dateDiff-($fullDays*60*60*24)-($fullHours*60*60))/60);

		//output in either:
		// if ( >= 365 days) year days
		// if (< 365 days) days
		// if ( < 1 day) hr min		( "2 hr 35 min" )
		if ($fullYears > 1)
			return $fullYears . " years " . ($fullDays - floor($fullYears * 365.25)) . " days";
		elseif ($fullYears > 0)
			return $fullYears . " year " . ($fullDays - floor($fullYears * 365.25)) . " days";
		elseif ($fullDays >= 2)
			return $fullDays . " days";
		elseif ($fullDays < 2 && $fullDays >= 1)
			return $fullDays . " day " . ($fullHours) . " hrs";
			# - floor($fullDays*24)
		elseif ($fullHours > 1)
			return $fullHours . " hrs " . ($fullMinutes) . " mins";
			#$fullMinutes - floor($fullHours*60)
		elseif ($fullHours == 1)
			return $fullHours . " hr " . ($fullMinutes) . " mins";
		else
			return $fullMinutes . " mins";
	}

	function printHTMLStory2($story)
	{
		//get domain
		$pattern = "^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,6}^";
		preg_match($pattern, $story->link, $matches);
		//var_dump($matches);

		echo "<div class=\"news-summary\" about=\"" . $story->href  . "\">";

		echo "<div class=\"news-body\"><h3><a href=\"" . $story->link . "\">" . $story->title . "</a></h3>";
		echo "<p><em class=\"source\">" . $matches[0] . " &mdash; </em>";
		echo "<span>" . $story->description;
		echo "<a href=\"" . $story->href . "\" class=\"more\">More &hellip; </a></span>";
		echo "<span class=\"topic\">(<a href=\"http://www.digg.com/" . $story->topic_short_name . "\">" . $story->topic_name . "</a>)</span></p>";
		echo "<div class=\"news-details\">";
		echo " <a href=\"" . $story->href . "\" class=\"comments\">" . $story->comments . " Comments</a>";
		echo "<span class=\"user-info\">";
		echo "<a href=\"http://www.digg.com/users/" . $story->user_name . "\"><img src=\"" . $story->user_icon . "\" alt=\"" . $story->user_name . "\" class=\"user-photo\" height=\"16\" width=\"16\">" . $story->user_name . "</a> ";

		showDate($story->status, $story->submit_date, $story->promote_date);
		echo " </span></div></div>";

		echo "<ul class=\"news-digg\"><li class=\"digg-count\">"; 
		echo "<a href=\"" . $story->href . "\" >" . $story->diggs . " diggs</a></li></ul></div>\n";

	}

	function printStoriesPaginator($pages, $addquery)
	{
		$query = "SELECT * from story_data " . $addquery . " ORDER BY submit_date DESC " . $pages->limit;
		$result = mysql_query($query) or die ('Error in query: $query. ' . mysql_error());

		if (mysql_num_rows($result) > 0)
		{
			while($row = mysql_fetch_object($result))
			{
				printHTMLStory2($row);
			}
		} else
		{
			echo "No Digg Articles Found!";
		}

		mysql_free_result($result);
	}
?>
