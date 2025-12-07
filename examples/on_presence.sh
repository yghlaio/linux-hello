#!/bin/bash
# Example script triggered when user presence is detected

# Event data is passed as environment variables:
# FACE_AUTH_EVENT - Event type
# FACE_AUTH_USERNAME - Detected username
# FACE_AUTH_CONFIDENCE - Recognition confidence
# FACE_AUTH_TIMESTAMP - Event timestamp

echo "User detected: $FACE_AUTH_USERNAME (confidence: $FACE_AUTH_CONFIDENCE)"

# Example: Send notification
notify-send "Welcome back!" "User $FACE_AUTH_USERNAME detected"

# Example: Resume music playback
# playerctl play

# Example: Unlock KeePassXC
# keepassxc-cli open /path/to/database.kdbx

# Add your custom actions here
