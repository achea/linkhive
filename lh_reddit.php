#!/usr/bin/php
<?php
// This program downloads liked/disliked/saved stories for a user into a MySQL database
// fetch liked (and saved?) stories for reddit user
//    comments?
//
// liked/disliked stories are only accessed by logging in, saved stories can be accessed by the public
//    if unliked (neutral) and then liked again, is the story now the most recent? or is it positioned in its original place?
//

function save_reddit_stories($data, $table)
{
	//{"kind": "t3", "data": {"domain": "huffingtonpost.com", "clicked": false, "name": "t3_8rad9", "ups": 33, "author": "shaggy0798", "url": "http://www.huffingtonpost.com/aaron-greenspan/the-facebook-another-prod_b_100662.html", "media": null, "downs": 2, "created": 1244648462.0, "created_utc": 1244648462.0, "subreddit_id": "t5_2qhlm", "subreddit": "education", "selftext": null, "likes": true, "num_comments": 3, "id": "8rad9", "title": "All around me I saw indications that many of the top young minds in the world were being trained, in essence, to study, but not to think. ", "hidden": false, "score": 31, "saved": false, "thumbnail": ""}}
	// kind domain clicked name ups author url media downs created created_utc subreddit_id subreddit selftext likes num_comments id title hidden score saved thumbnail
	
	$i = 0;
	$num_saved = 0;
	$status = false;
	$json = json_decode($data);
	$num_stories = count($json->data->children);

	$story_ids = array();

	// detect dupes
	for ($i = 0; $i < $num_stories; $i++)
	{
		$story_ids[$i] = "'" . $json->data->children[$i]->data->id . "'";
	}
	$query = "SELECT COUNT(*) FROM " . $table . " WHERE id IN (" . implode(",", $story_ids) . ")"; 
	$status = mysql_query($query);
	$row = mysql_fetch_array($status, MYSQL_NUM);
	$num_dupes = $row[0];
	// print $num_dupes . " dupes \n";

	for ( $i = 0; $i < $num_stories;  $i++)
	{
		$query = format_insert_query($json->data->children[$i], $table);
		$status = mysql_query($query);
		if (!$status)
		{
			print "Failed [ " . $i . " ] " . $json->data->children[$i]->data->title . "\n";
			print $query . "\n";
		} else 
		{
			$num_saved++;
		}
		
	}

	return array('after' => $json->data->after, 'dupes' => $num_dupes, 'saved' => $num_saved);
}

function format_insert_query($story, $table)
{
	// assume that the returned json data has addslashes already run on it
		// guess not... 
	$query = "INSERT INTO " . $table . " VALUES ('" . $story->kind . "', '" . $story->data->domain . "', " . isset_bool($story->data->clicked) . ", '" . $story->data->name . "', " . $story->data->ups . ", '" . $story->data->author . "', '" . addslashes($story->data->url) . "'," . isset_null($story->data->media) . ", " . $story->data->downs . ", " . $story->data->created . ", " . $story->data->created_utc . ", '" . $story->data->subreddit_id . "', '" . $story->data->subreddit . "'," . isset_null($story->data->selftext) . ", " . isset_bool($story->data->likes) . ", " . $story->data->num_comments . ", '" . $story->data->id . "', '" . addslashes($story->data->title) . "', " . isset_bool($story->data->hidden) . ", " . $story->data->score . ", " . isset_bool($story->data->saved) . ", '" . $story->data->thumbnail . "') ON DUPLICATE KEY UPDATE clicked=VALUES(clicked), ups=VALUES(ups), downs=VALUES(downs), likes=VALUES(likes), num_comments=VALUES(num_comments), hidden=VALUES(hidden), score=VALUES(score), saved=VALUES(saved)";

	return $query;
}

function isset_bool($var)
{
	// return strings 
	if (is_null($var))
		return "null";
	return ($var ? "true" : "false");

}

function isset_null($var)
{
	// return string null instead of null
	return ($var != null ? "'" . addslashes($var) . "'" : "null");
}

	$mysql_user = "achea";
	$mysql_db = "lh_reddit";
	$mysql_pass = "asdf";
	$mysql_reddit_table = "reddit_stories";		// extract ids from this one table

	$reddit_loginurl="http://www.reddit.com/post/login";
	$reddit_baseuserurl="http://www.reddit.com/user/";
	$reddit_user="Gambit89";
	$reddit_pass="";		// read from file
	$reddit_liked="/liked/";
	$reddit_json=".json";

	$reddit_pass_file="reddit_pass";
	$reddit_cookie_file="/tmp/lh_reddit_cookie";

	$user_agent = "Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.0.11) Gecko/2009071103 Gentoo Firefox/3.0.11";

	if (file_exists($reddit_pass_file))
	{
		$handle = fopen($reddit_pass_file, "r");
		$data = fgets($handle); 
		$reddit_pass = rtrim($data);			// remove endl
		fclose($handle);
	} else
	{
		die ("Reddit pass file does not exist\n");
	}

	mysql_connect(localhost,$mysql_user,$mysql_pass);
	@mysql_select_db($mysql_db) or die( "Unable to select database " . $mysql_db . "\n");
	$isstrictmode = mysql_query("SET sql_mode='STRICT_ALL_TABLES'");		//generate an error when can't insert
	if (!$isstrictmode)
		print "Not strict mode\n";

	//{"kind": "t3", "data": {"domain": "huffingtonpost.com", "clicked": false, "name": "t3_8rad9", "ups": 33, "author": "shaggy0798", "url": "http://www.huffingtonpost.com/aaron-greenspan/the-facebook-another-prod_b_100662.html", "media": null, "downs": 2, "created": 1244648462.0, "created_utc": 1244648462.0, "subreddit_id": "t5_2qhlm", "subreddit": "education", "selftext": null, "likes": true, "num_comments": 3, "id": "8rad9", "title": "All around me I saw indications that many of the top young minds in the world were being trained, in essence, to study, but not to think. ", "hidden": false, "score": 31, "saved": false, "thumbnail": ""}}
	$query= "CREATE TABLE IF NOT EXISTS " . $mysql_reddit_table .
"(
	kind			VARCHAR(3) CHARACTER SET utf8,
	domain			VARCHAR(60) CHARACTER SET utf8,
	clicked			BOOL,
	name			VARCHAR(11) CHARACTER SET utf8,
	ups				INT(11) UNSIGNED NOT NULL,
	author			VARCHAR(21) CHARACTER SET utf8,
	url				VARCHAR(2000) CHARACTER SET utf8,
	media			VARCHAR(400) CHARACTER SET utf8,
	downs			INT(11) UNSIGNED NOT NULL,
	created			FLOAT UNSIGNED NOT NULL,
	created_utc		FLOAT UNSIGNED NOT NULL,
	subreddit_id	VARCHAR(11) CHARACTER SET utf8,
	subreddit		VARCHAR(21) CHARACTER SET utf8,
	selftext		MEDIUMTEXT CHARACTER SET utf8,
	likes			BOOL,
	num_comments	INT(11) UNSIGNED NOT NULL,
	id				VARCHAR(11) CHARACTER SET utf8,
	title			VARCHAR(300) CHARACTER SET utf8,
	hidden			BOOL,
	score			INT(11) NOT NULL,
	saved			BOOL,
	thumbnail		VARCHAR(60) CHARACTER SET utf8,
	PRIMARY KEY		(id)
)";
	$status = mysql_query($query);
	if (!$status)
	{
		die("Unable to create " . $mysql_reddit_table . " table");
	}

//	var_dump($reddit_pass);
//	print "done";
//	exit(1);

	if (!file_exists($reddit_cookie_file))
	{
		print "Logging in...\n";
		$ch = curl_init();			//initialize cURL session
		curl_setopt($ch, CURLOPT_URL, $reddit_loginurl);
		curl_setopt($ch, CURLOPT_MAXREDIRS, 5);			//recommended as leeway for redirections
		curl_setopt($ch, CURLOPT_FOLLOWLOCATION, 1);		//recommend for redirection

		curl_setopt($ch, CURLOPT_POST, 1);
		curl_setopt($ch, CURLOPT_POSTFIELDS, "user=" . $reddit_user . "&passwd=" . $reddit_pass);
		curl_setopt($ch, CURLOPT_COOKIEJAR, $reddit_cookie_file);		// save on close?
		curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);

		$result = curl_exec($ch);
		curl_close($ch);	
		//print $result;
	} else
	{
		print "Using previous login cookie...\n";
	}
	
	// assume that the login worked
	// how to die if not logged in?
		// how to check if logged in (just because we checked doesn't mean we know?)

	print "Downloading stories...\n";
	// what happens to CURLOPTs after an exec?
		// assume that they are kept
	$ch = curl_init();
	$reddit_likedurl = $reddit_baseuserurl . $reddit_user . $reddit_liked . $reddit_json;
	curl_setopt($ch, CURLOPT_URL,
		$reddit_likedurl);
	curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
	// curl_setopt($ch, CURLOPT_POST, 0);
	curl_setopt($ch, CURLOPT_COOKIEFILE, $reddit_cookie_file);		// 
	// curl_setopt($ch, CURLOPT_VERBOSE, 1);
	// curl_setopt($ch, CURL_USERAGENT, $user_agent);

	$curlPostAfter = "";
	$curlPostCount = "?count=100";
	$curlPost = $curlPostCount;
	$saved = 0;

	print "URL: " . $reddit_baseuserurl . $reddit_user . $reddit_liked . $reddit_json . "\n";


	do
	{
		// fetch the first page
			// if after != null; then there is more to go, so loop with after POST
		curl_setopt($ch, CURLOPT_URL, $reddit_likedurl . $curlPost);
		$data = curl_exec($ch);

		// print $data;
		// print_r(curl_getinfo($ch)); 
		// echo "\n\ncURL error number:" .curl_errno($ch); 
		// echo "\ncURL error:" . curl_error($ch);  
		
		// data is json format
		// assume that it works
			// how to check if it doesn't?
		$status = save_reddit_stories($data, $mysql_reddit_table);
		$saved += $status['saved'];
		print $saved . " ... ";
		if ($status['after'] != null && $status['dupes'] != true)
		{
			$curlPost = $curlPostCount . "&after=" . $status['after'];
			sleep(3);
		}

		// status has after and dupes
			// dupes is when 100 dupes were detected, then it should be safe enough to say that we can quit
				// a full page of dupes were retrieved
				// assumes that count = 100
			// assume that return newest first, oldest has after == null
	} while ($status['after'] != null && $status['dupes'] < 100 );

	curl_close($ch); 
	unset($ch);
	mysql_close();

	// php parse json

?>
