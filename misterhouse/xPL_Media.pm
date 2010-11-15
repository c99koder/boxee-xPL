=begin comment
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

xPL_Media.pm - xPL support for the Media.Basic schema

Info:

  This module allows to easily integrate xPL media devices in your MH setup.
  
License:
  This free software is licensed under the terms of the GNU public license.

Authors:
  Sam Steele

@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
=cut

use strict;

package xPL_Media;
@xPL_Media::ISA = ('xPL_Item');

sub new {
    my ($class, $source) = @_;
    my $self = $class->SUPER::new($source);
    $self->SUPER::class_name('media.*');
	$self->restore_data('title');
	$self->restore_data('artist');
	$self->restore_data('album');
	$self->restore_data('duration');
	$self->restore_data('format');
	$self->restore_data('kind');
	&::print_log("[xPL_Media] Created device $source") if $main::Debug{xpl_media};
	
    return $self;
}

sub title {
    my ($self) = @_;
	return $$self{title};
}

sub artist {
    my ($self) = @_;
	return $$self{artist};
}

sub album {
    my ($self) = @_;
	return $$self{album};
}

sub duration {
    my ($self) = @_;
	return $$self{duration};
}

sub format {
    my ($self) = @_;
	return $$self{format};
}

sub kind {
    my ($self) = @_;
	return $$self{kind};
}

# Craft a message to request the state and media of all media devices
sub request_all_stat {
   	&xPL::sendXpl('*', 'cmnd', 'media.request' => { 'request' => 'mptrnspt' });
   	&xPL::sendXpl('*', 'cmnd', 'media.request' => { 'request' => 'mpmedia' });
}

# Request the status of the device
sub request_stat {
    my ($self) = @_;
    $self->SUPER::send_cmnd('media.request' => { 'request' => 'mptrnspt' });
    $self->SUPER::send_cmnd('media.request' => { 'request' => 'mpmedia' });
}

sub id {
    my ($self) = @_;
    return $$self{id};
}

sub ignore_message {
    my ($self, $p_data) = @_;
    my $ignore_msg = 0;
    if (!(defined($$p_data{'media.mptrnspt'})) && !(defined($$p_data{'media.mpmedia'}))  ){
		$ignore_msg = 1;
    }
    return $ignore_msg;
}

sub set_now
{
    my ($self, $p_state, $set_by) = @_;
	my $state = 'unknown';

    if ($set_by =~ /^xpl/i) {
    	if ($$self{changed} =~ /media\.mptrnspt/) {
			$state = $$self{'media.mptrnspt'}{'command'};
			if($state eq 'stop') {
				$$self{'title'} = undef;
				$$self{'artist'} = undef;
				$$self{'album'} = undef;
				$$self{'duration'} = undef;
				$$self{'kind'} = undef;
			}
		} elsif ($$self{changed} =~ /media\.mpmedia/) {
			$$self{'title'} = $$self{'media.mpmedia'}{'title'};
			$$self{'artist'} = $$self{'media.mpmedia'}{'artist'};
			$$self{'album'} = $$self{'media.mpmedia'}{'album'};
			$$self{'duration'} = $$self{'media.mpmedia'}{'duration'};
			$$self{'kind'} = $$self{'media.mpmedia'}{'kind'};
			$state = 'play';
		}
    } else {
    	return -1 if ($self->state eq $p_state); # Don't propagate state unless it has changed.
        
   		$self->SUPER::send_cmnd('media.basic' => {'command' => $p_state});
    }

	$self->SUPER::set_now($state, $set_by) unless $state eq 'unknown';
	return;
}
