#!/usr/bin/php

<?php

//Tables of
//diggs from user
//information (title, url, description, etc) on digg stories
//users who dugg each digg story
//comments on each digg story

function get_missing_stories($userDiggs, $userDiggCount, $stories, $storyCount)
{
	// all of the fetched diggs are in story_data
	// unfetched are those that are in my dugg table, but not in story_data

	// query all from both, zero out fetched in dugg table
	//    non-zeroed out are those that are unfetched

	$userDiggIDs = array ();		//empty array
	for ($i = 0; $i < $userDiggCount; $i++)
	{
		$row = mysql_fetch_array($userDiggs, MYSQL_NUM);
		$userDiggIDs[$i] = $row[0];		//extract to second array
	}

	$storyIDs = array ();		//empty array
	for ($i = 0; $i < $storyCount; $i++)
	{
		$row = mysql_fetch_array($stories, MYSQL_NUM);
		$storyIDs[$i] = $row[0];		//extract to second array
	}

	$missing = array_diff($userDiggIDs,$storyIDs);		//yay, php has this function

	return $missing;
}

function update_maximums($maximums, $story)
{
	if ($maximums['link'] < strlen($story->link))
		$maximums['link'] = strlen($story->link);
	if ($maximums['href'] < strlen($story->href))
		$maximums['href'] = strlen($story->href);
	if ($maximums['title'] < strlen($story->title))
		$maximums['title'] = strlen($story->title);
	if ($maximums['description'] < strlen($story->description))
		$maximums['description'] = strlen($story->description);
	if ($maximums['tnsrc'] < strlen($story->thumbnail->src))
		$maximums['tnsrc'] = strlen($story->thumbnail->src);

	return $maximums;
}

function fetch_stories ($storyIDs, $mysqlStoryTable)
{
	//the mysql_fetch_array keeps track of stories fetch so that I didn't have to make another variable to do that
	//	now I do

	//get all stories in database
	//while still stories
	//if (numstories < 100) fetch numstories; else fetch 100
	//get stories and load to array
	//get story data
	//for each story
	//save into database

	$maximums = array( 'link' => 0 , 'href' => 0, 'title' => 0, 'description' => 0, 'tnsrc' => 0);
	try {
		$api = Services_Digg::factory('Stories');

		/*$countStories = 0;						//storyid counter
		while ($row = mysql_fetch_array($storyIDs, MYSQL_NUM)) {
			$storyIDs[$countStories] = $row[0];			//save ids into array
			$countStories++;
		}

		if ($numStories != $countStories) print "not matching counts";*/

		$countStories = $numStories = count($storyIDs);
		$savedStories = 0;
		print "Saved ... ";
		while ($countStories > 0)
		{
			sleep(2);
			$fetchCount = ( $countStories < 100 ? $countStories : 100);	//100 max from api
			//print $countStories;
			//extract
			/*$subStoryIDs = array ();		//empty array
			for ($i = 0; $i < $fetchCount; $i++)
			{
				$row = mysql_fetch_array($storyIDs, MYSQL_NUM);
				$subStoryIDs[$i] = $row[0];		//extract to second array
			}*/
			$subStoryIDs = array_slice($storyIDs, $numStories - $countStories, $fetchCount);
			//print_r($subStoryIDs);
			//print "\n" . count($subStoryIDs);

			//now storyids should have enough story ids
			//call api
			$params = array( 'count' => 100 );
			$stories = $api->getStoriesById($subStoryIDs, $params);

			//print $stories->total . " " . $stories->count . " " . $stories->offset ;
			if ($fetchCount != $stories->total) print "Fetch did not match total\n";
			$x = 0;
			foreach ($stories as $story)
			{
				$maximums = update_maximums($maximums, $story);
				//save each story
				$query = format_insert_story_query($story, $mysqlStoryTable);
				$status = mysql_query($query);
				if ($status)
				{
					$x++;			//save story counter
				} else {
					//One problem was that I did not add slashes to quotes in link, title, description
					print "\n--- Did not save " . $story->title . "\n";
					//var_dump($story);
					print $query . "\n";
					//print $story->status . "\n";
				}
			}

			$savedStories += $x;
			//print "Did not save " . (100-$x) . " stories\n";
			print $savedStories . " ... ";
			$countStories -= $fetchCount;		//decrement counter
		}

	} catch (PEAR_Exception $error) {
		echo $error->getMessage() . "\n";
	} catch (Services_Digg_Exception $error) {
		echo $error . '\n';
	}

	var_dump($maximums);
	
	return $savedStories;
}

function format_insert_story_query ($story, $mysqlStoryTable)
{
	//var_dump($story);

	//print $story->href . " | " . $story->user->name . " " .  $story->thumbnail->src . "\n";

	$query = "INSERT INTO " . $mysqlStoryTable . " VALUES (" . $story->id . ",'" . addslashes($story->link) . "'," . $story->submit_date . "," . $story->diggs . "," . $story->comments . "," . (isset($story->promote_date) ? $story->promote_date : NULL) . ",'" . $story->status . "','" . $story->media . "','" . $story->href . "','" . addslashes($story->title) . "','" . addslashes($story->description) . "','" . $story->user->name . "','" . $story->user->icon;

	//inactive user or no user 
	if (!strcmp($story->user->name,"inactive") || !strcmp($story->user->name,''))
	{
		$query .= "',NULL,NULL";
	} else {
		$query .= "'," . $story->user->registered . "," . $story->user->profileviews; 
	}
	$query .= ",'" . $story->topic->name . "','" . $story->topic->short_name . "','" . $story->container->name . "','" . $story->container->short_name;
	//missing thumbnail
	if (isset($story->thumbnail))
	{
		$query .= "'," . $story->thumbnail->originalwidth . "," . $story->thumbnail->originalheight . ",'" . $story->thumbnail->contentType . "','" . $story->thumbnail->src . "'," . $story->thumbnail->width . "," . $story->thumbnail->height . ")";
	} else {
		$query .= "',NULL,NULL,'','',NULL,NULL)";
	}
	//print $query;
	return $query;
}

//open mysql connection
//check if update, or full fetch

	$mysqlUser="achea";
	$mysqlPassword="asdf";
	$mysqlDatabase="lh_digg";

	$diggUser="Gambit89";		//later do dynamic
	$mysqlDiggsTable = "diggs_" . $diggUser;
	$mysqlStoryTable = "story_data";
	$mysqlStoryDiggsTable = "story_diggs";

	require_once 'Services/Digg.php';
	ini_set('user_agent', 'linkhive/0.1');
	Services_Digg::$appKey = 'http://www.achea.org/';

//	echo $argc;
//	for ($x = 0; $x < $argc; $x++)
//		echo $argv[$x];

	if ($argc < 2)				//if less than two arguments (script name, command)
		die($argv[0] . " [update|fetch|create]\n"); 
	$command = $argv[1];			//get the command

	//open mysql
	mysql_connect(localhost,$mysqlUser,$mysqlPassword);
	@mysql_select_db($mysqlDatabase) or die( "Unable to select database " . $mysqlDatabase);
	//$isstrictmode = mysql_query("SET sql_mode='STRICT_ALL_TABLES'");		//generate an error when can't insert 
	//if (!$isstrictmode)
	//	print "Not strict mode\n";

	switch ($command):
		case "update":
			print "Updating caches...";
			break;
		case "fetch-diggs":
			print "Fetching diggs ...";
			//from the beginning
			//assumed the profile does not edit during the fetch

			//get initial and step back
			try {
				$params = array('count' => 100, 'offset' => 0);

				$api = Services_Digg::factory('Users');

				$numDupes = 0;
				$numSaved = 0;

				do {
					sleep(2);		//sleep for 1 second
					print $diggs->offset . "\n";

					$diggs = $api->getUsersDiggs(array($diggUser), $params);		//needs array as param
					//store it into sql

					foreach ($diggs as $digg)
					{
						//is the digg a duplicate in the table?
						$query = "SELECT * FROM " . $mysqlDiggsTable . " WHERE story IN (". $digg->story . ")";

						$result = mysql_query($query);
						$numRows = mysql_numrows($result);
						//if there is a row, then it is a duplicate

						if ($numRows >= 1)
						{
							print "Skipping duplicate story " . $digg->story . "\n";
							$numDupes++;
						} elseif ($numRows == 0)	//not yet in database
						{
							//so save it
							$query = "INSERT into " . $mysqlDiggsTable . " VALUES (" . $digg->date . "," . $digg->story . "," . $digg->id . ",'" . $digg->user . "','" . $digg->status . "')";
							//print $query . "\n";
							mysql_query($query);
							$numSaved++;
						} else
						{
							print "You should never see this line.\n";
						}

					}
					if ($diggs->offset + $diggs->count < $diggs->total)
					{
						//diggs count should be 100 always
						$params['offset'] = $diggs->offset + $diggs->count;
					}
					//if offset + count > total, that's all the diggs
				} while ($diggs->offset + $diggs->count < $diggs->total);
				/*echo '<ul>';
				foreach ($user->diggs($params) as $digg) {
					$story = Services_Digg::factory('Stories')->getStoryById($digg->story);
					echo '<li><a href="' . $story->href . '">' . $story->title . '</li>';
				}
				echo '</ul>';*/

				/*foreach ($diggs as $digg)
				{
					$story = Services_Digg::factory('Stories')->getStoryById($digg->story);
					echo $story->title,"\n";
				}*/
				//print $diggs->total . " " . $diggs->timestamp . " " . $diggs->offset . $diggs->min_date;
				print " done.\nStories saved: " . $numSaved . "\nDuplicates: " . $numDupes . "\n";
			} catch (PEAR_Exception $error) {
				echo $error->getMessage() . "\n";
			} catch (Services_Digg_Exception $error) {
				echo $error . '\n';
			}

			break;
		case "fetch-story-data":
			//fetch the story data from database
			//should overwrite

			//the mysql_fetch_array keeps track of stories fetch so that I don't have to make another variable to do that

			//get all stories in database
			//while still stories
				//if (numstories < 100) fetch numstories; else fetch 100
				//get stories and load to array
				//get story data
				//for each story
					//save into database

			$result = mysql_query("SELECT story FROM " . $mysqlDiggsTable);
			$numStories = mysql_num_rows($result);

			$storyIDs = array ();		//empty array
			for ($i = 0; $i < $numStories; $i++)
			{
				$row = mysql_fetch_array($result, MYSQL_NUM);
				$storyIDs[$i] = $row[0];		//extract to second array
			}

			$savedStories = fetch_stories($storyIDs, $mysqlStoryTable);

			print "\n---\nTotal # of stories: " . $numStories . "\nStories saved: " . $savedStories . "\nStories not saved: " . ($numStories - $savedStories) . "\n";

			break;
		case "update-story-data":
			break;
		case "fetch-missing-stories":

			$result1 = mysql_query("SELECT story FROM " . $mysqlDiggsTable);
			$userDiggsCount = mysql_num_rows($result1);
			$result2 = mysql_query("SELECT id FROM " . $mysqlStoryTable);
			$storyCount = mysql_num_rows($result2);
			if ($storyCount < $userDiggsCount)
			{
				$missing = get_missing_stories($result1, $userDiggsCount, $result2, $storyCount);
				//var_dump($missing);
				$numMissing = count($missing);
				print "Missing " . $numMissing . " | " . ($userDiggsCount - $storyCount) . " stories\n";
				$savedStories = fetch_stories($missing, $mysqlStoryTable);
				print "\n---\nTotal # of stories: " . $userDiggsCount . "\nPreviously missing stories: " . $numMissing . "\nStories saved: " . $savedStories . "\nStories still missing: " . ($numMissing - $savedStories) . "\n";
			} elseif ($storyCount == $userDiggsCount) {
				echo "All stories are fetched!\n";
			} else {
				echo "There are extra stories saved that were not dugg.\n";
			}

			break;
		case "create-diggs-table":
			//if exists mysql digg_php table, prompt for deletion
			print "Creating MySQL table for dugg stories...";

			//this is an example line from a /diggs endpoint request

			// <digg date="1207098435" story="5939299" id="133463245" user="Gambit89" status="popular" />
			$query= "CREATE TABLE " . $mysqlDiggsTable .
"(
	date     INT(11) UNSIGNED NOT NULL,
	story INT(20) UNSIGNED NOT NULL,
	id	INT(20) UNSIGNED NOT NULL,
	user	CHAR(20) CHARACTER SET utf8,
	status	CHAR(10) CHARACTER SET utf8,
	PRIMARY KEY (id)
)";
			$status = mysql_query($query);
			$message = ( $status? "Success!\n" : "Table not created\n" );
			print $message;
			break;
		case "create-stories-table":
			print "Creating MySQL table for story data...";

			//this is an example line from a /diggs endpoint request
/* <story id="4368401" link="http://maxsangalli.altervista.org/?p=45" submit_date="1196891534" diggs="1" comments="0" status="upcoming" media="news" href="http://digg.com/linux_unix/Jukebox_con_Linux">
  <title>Jukebox con Linux</title>
  <description>Jukebox with Linux</description>
  <user name="ilsanga" icon="http://digg.com/img/udl.png" registered="1196891377" profileviews="0" />
  <topic name="Linux/Unix" short_name="linux_unix" />
  <container name="Technology" short_name="technology" />
  <thumbnail originalwidth="390" originalheight="387" contentType="image/jpeg" src="http://digg.com/linux_unix/Jukebox_con_Linux/t.jpg" width="80" height="80" />
 </story> */

			//url has length of 255, title has length of 66 chars, description has length of 350 chars.
			// CREATE TABLE IF NOT EXISTS
			$query= "CREATE TABLE " . $mysqlStoryTable .
"(
	id		INT(20) UNSIGNED NOT NULL,
	link		VARCHAR(257) CHARACTER SET utf8,
	submit_date     INT(20) UNSIGNED NOT NULL,
	diggs		INT(11) UNSIGNED NOT NULL,
	comments	INT(11) UNSIGNED NOT NULL,
	promote_date	INT(20) UNSIGNED,
	status		VARCHAR(10) CHARACTER SET utf8,
	media		VARCHAR(20) CHARACTER SET utf8,
	href		VARCHAR(130) CHARACTER SET utf8,

	title		VARCHAR(66) CHARACTER SET utf8,
	description	VARCHAR(352) CHARACTER SET utf8,
	user_name	VARCHAR(20) CHARACTER SET utf8,
	user_icon	VARCHAR(60) CHARACTER SET utf8,
	user_registered	INT(20) UNSIGNED,
	user_profileviews	INT(11) UNSIGNED,
	topic_name	VARCHAR(30) CHARACTER SET utf8,
	topic_short_name	VARCHAR(20) CHARACTER SET utf8,
	container_name	VARCHAR(30) CHARACTER SET utf8,
	container_short_name	VARCHAR(20) CHARACTER SET utf8,
	thumbnail_originalwidth	INT(10) UNSIGNED,
	thumbnail_originalheight	INT(10) UNSIGNED,
	thumbnail_contentType	VARCHAR(20) CHARACTER SET utf8,
	thumbnail_src	VARCHAR(60) CHARACTER SET utf8,
	thumbnail_width	INT(10) UNSIGNED,
	thumbnail_height	INT(10) UNSIGNED,
	PRIMARY KEY (id)
)";
			$status = mysql_query($query);
			$message = ( $status? "Success!\n" : "Error: Table not created\n" );
			print $message;
			break;
		case "create-story-diggs-table":
			// plan to use for friend-finding
			//    once the computer can look up stories that I mark important
			print "Creating table for diggs of stories... ";
			$query= "CREATE TABLE " . $mysqlStoryDiggsTable .
"(
	date     INT(11) UNSIGNED NOT NULL,
	story INT(20) UNSIGNED NOT NULL,
	id	INT(20) UNSIGNED NOT NULL,
	user	CHAR(20) CHARACTER SET utf8,
	status	CHAR(10) CHARACTER SET utf8,
	PRIMARY KEY (id)
)";
			$status = mysql_query($query);
			$message = ( $status? "Success!\n" : "Error: Table not created\n" );
			print $message;
			break;
		case "create-comments-table":
		case "help":
		default:
			print "Bad command.\n";
	endswitch;

	mysql_close();

?>
