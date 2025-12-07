#!/bin/bash
# Example script triggered when user absence is detected

# Event data is passed as environment variables:
# FACE_AUTH_EVENT - Event type
# FACE_AUTH_USERNAME - Last detected username
# FACE_AUTH_ABSENCE_DURATION - How long user was absent (seconds)
# FACE_AUTH_TIMESTAMP - Event timestamp

echo "User absent: $FACE_AUTH_USERNAME (duration: $FACE_AUTH_ABSENCE_DURATION seconds)"

# Example: Send notification
notify-send "User Absent" "Locking system..."

# Example: Pause music playback
# playerctl pause

# Example: Lock password manager
# keepassxc-cli lock

# Example: Mute microphone
# pactl set-source-mute @DEFAULT_SOURCE@ 1

# Add your custom actions here
