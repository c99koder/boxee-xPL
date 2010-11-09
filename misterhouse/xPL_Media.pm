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
use base qw(xPL_Item);

sub new {
    my ($class, $p_source) = @_;
    my $source = $p_source;
    my $self = $class->SUPER::new($source);
    $self->SUPER::class_name('media.*');
	$$self{state_monitor} = "media.mptrnspt : command";
	&::print_log("[xPL_Media] Created device $source") if $main::Debug{xpl_media};
	
    return $self;
}

sub title {
    my ($self) = @_;
	return $$self{'media.mpmedia'}{title};
}

sub artist {
    my ($self) = @_;
	return $$self{'media.mpmedia'}{artist};
}

sub album {
    my ($self) = @_;
	return $$self{'media.mpmedia'}{album};
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

sub default_setstate
{
    my ($self, $state, $substate, $set_by) = @_;
    if ($set_by =~ /^xpl/i) {
    	if ($$self{changed} =~ /media\.mptrnspt/) {
           &::print_log("[xpl_media] " . $self->get_object_name
                . " state is $state") if $main::Debug{xpl_media};
    	   return -1 if $self->state eq $state; # don't propagate state unless it has changed#
		}
    } else {
    	return -1 if ($self->state eq $state); # Don't propagate state unless it has changed.
        &::print_log("[xpl_media] Request " . $self->get_object_name . " " . $state) if $main::Debug{xpl_media};
        
   		$self->SUPER::send_cmnd('media.basic' => {'command' => $state});#

    	return;
    }
	
}
    
1;
