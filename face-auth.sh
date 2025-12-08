#!/bin/bash
# Bash wrapper for face authentication system
# Use this in your bash scripts for face authentication

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PYTHON="$SCRIPT_DIR/venv/bin/python3"
CLI_SCRIPT="$SCRIPT_DIR/cli.py"

# Check if venv exists
if [ ! -f "$VENV_PYTHON" ]; then
    echo "Error: Virtual environment not found. Please run install.sh first." >&2
    exit 1
fi

# Function: Authenticate user
# Returns: 0 if authenticated, 1 if not
# Sets: FACE_AUTH_USER and FACE_AUTH_CONFIDENCE environment variables
face_auth() {
    local timeout="${1:-10}"
    
    # Run authentication
    output=$("$VENV_PYTHON" "$CLI_SCRIPT" test --timeout "$timeout" --no-preview 2>&1)
    exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        # Extract username and confidence from output
        export FACE_AUTH_USER=$(echo "$output" | grep "User:" | awk '{print $2}')
        export FACE_AUTH_CONFIDENCE=$(echo "$output" | grep "Confidence:" | awk '{print $2}')
        return 0
    else
        unset FACE_AUTH_USER
        unset FACE_AUTH_CONFIDENCE
        return 1
    fi
}

# Function: Check if user is enrolled
# Args: username
# Returns: 0 if enrolled, 1 if not
face_is_enrolled() {
    local username="$1"
    
    if [ -z "$username" ]; then
        echo "Usage: face_is_enrolled <username>" >&2
        return 2
    fi
    
    "$VENV_PYTHON" "$CLI_SCRIPT" list 2>&1 | grep -q "👤 $username"
    return $?
}

# Function: Get list of enrolled users
# Returns: List of usernames (one per line)
face_list_users() {
    "$VENV_PYTHON" "$CLI_SCRIPT" list 2>&1 | grep "👤" | awk '{print $2}'
}

# Function: Enroll a new user
# Args: username [num_samples]
# Returns: 0 if successful, 1 if failed
face_enroll() {
    local username="$1"
    local samples="${2:-5}"
    
    if [ -z "$username" ]; then
        echo "Usage: face_enroll <username> [num_samples]" >&2
        return 2
    fi
    
    "$VENV_PYTHON" "$CLI_SCRIPT" enroll "$username" --samples "$samples"
    return $?
}

# Function: Remove enrolled user
# Args: username
# Returns: 0 if successful, 1 if failed
face_remove() {
    local username="$1"
    
    if [ -z "$username" ]; then
        echo "Usage: face_remove <username>" >&2
        return 2
    fi
    
    "$VENV_PYTHON" "$CLI_SCRIPT" remove "$username"
    return $?
}

# Function: Get system status
# Returns: Status information
face_status() {
    "$VENV_PYTHON" "$CLI_SCRIPT" status
}

# If script is sourced, export functions
if [ "${BASH_SOURCE[0]}" != "${0}" ]; then
    export -f face_auth
    export -f face_is_enrolled
    export -f face_list_users
    export -f face_enroll
    export -f face_remove
    export -f face_status
    echo "Face authentication functions loaded. Available commands:"
    echo "  face_auth [timeout]           - Authenticate user"
    echo "  face_is_enrolled <username>   - Check if user is enrolled"
    echo "  face_list_users               - List enrolled users"
    echo "  face_enroll <username> [samples] - Enroll new user"
    echo "  face_remove <username>        - Remove user"
    echo "  face_status                   - Show system status"
else
    # If executed directly, show usage
    cat << 'EOF'
Face Authentication Bash Library

Usage:
  Source this file in your bash script:
    source /opt/linux-hello/face-auth.sh

Available Functions:
  face_auth [timeout]
    Authenticate user via face recognition
    Returns: 0 if authenticated, 1 if not
    Sets: FACE_AUTH_USER and FACE_AUTH_CONFIDENCE variables
    
    Example:
      if face_auth 10; then
        echo "Welcome $FACE_AUTH_USER (confidence: $FACE_AUTH_CONFIDENCE)"
      else
        echo "Authentication failed"
      fi

  face_is_enrolled <username>
    Check if a user is enrolled
    Returns: 0 if enrolled, 1 if not
    
    Example:
      if face_is_enrolled "alice"; then
        echo "Alice is enrolled"
      fi

  face_list_users
    List all enrolled users
    Returns: Usernames (one per line)
    
    Example:
      for user in $(face_list_users); do
        echo "User: $user"
      done

  face_enroll <username> [num_samples]
    Enroll a new user
    Returns: 0 if successful, 1 if failed
    
    Example:
      face_enroll "alice" 5

  face_remove <username>
    Remove an enrolled user
    Returns: 0 if successful, 1 if failed
    
    Example:
      face_remove "alice"

  face_status
    Show system status
    
    Example:
      face_status

Examples:
  # Simple authentication check
  source face-auth.sh
  if face_auth; then
    echo "Access granted to $FACE_AUTH_USER"
  else
    echo "Access denied"
    exit 1
  fi

  # Conditional script based on user
  source face-auth.sh
  if face_auth 15; then
    case "$FACE_AUTH_USER" in
      alice)
        echo "Running Alice's script..."
        ;;
      bob)
        echo "Running Bob's script..."
        ;;
      *)
        echo "Unknown user"
        ;;
    esac
  fi

EOF
fi
