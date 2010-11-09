# Category=Media

# Creates a Boxee xPL object and sets up state monitoring and defines several voice commands
# replace 'YOUR_HOSTNAME_HERE' with the hostname of the computer running Boxee

use xPL_Media;

$boxee = new xPL_Media("c99org-boxee.YOUR_HOSTNAME_HERE"); # noloop

$sb_status_req_timer = new Timer; # noloop
set $sb_status_req_timer 10;      # noloop

$boxee->manage_heartbeat_timeout(360, "speak 'Boxee is offline'", 1); # noloop

if ($state = state_now $boxee){
	print_log "+++ State event on boxee, state is " . $state;
	# You can put fancy state events in here, such as dimming the lights when the state changes to "play"
}
   
if (expired $sb_status_req_timer) {
	set $sb_status_req_timer 60;
	xPL_Media::request_all_stat();
}

# Voice commands
$v_what_playing = new Voice_Cmd('[What track is,What song is,Show track,Show song] playing now');

if (said $v_what_playing) {
	if($boxee->state() eq "play") {
		$v_what_playing->respond("app=boxee " . $boxee->title() . " by " . $boxee->artist());
	} else {
		$v_what_playing->respond("app=boxee Nothing is currently playing.");
	}
}

$v_boxee_cmd = new Voice_Cmd('[play,pause,stop,skip] {media player,media,music,to the next track,to the next song}');

if ($state = said $v_boxee_cmd) {
	$boxee->set_now($state);
}

