#!/usr/bin/env python3
"""
Command-line interface for Face Authentication System
"""

import argparse
import sys
import logging
from pathlib import Path
import subprocess
import os

from config import get_config, reload_config
from models import Database
from face_auth import FaceAuthenticator

logger = logging.getLogger(__name__)


def setup_logging(verbose: bool = False):
    """Setup logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )


def cmd_enroll(args):
    """Enroll a new user"""
    config = get_config()
    config.ensure_directories()
    
    db = Database(config.get('database.path'))
    authenticator = FaceAuthenticator(db)
    
    username = args.username or os.getenv('USER', 'user')
    
    print(f"\n{'='*60}")
    print(f"Face Authentication - User Enrollment")
    print(f"{'='*60}\n")
    
    success = authenticator.enroll_user(
        username=username,
        num_samples=args.samples,
        show_preview=not args.no_preview
    )
    
    if success:
        print(f"\n✅ Enrollment successful!")
        return 0
    else:
        print(f"\n❌ Enrollment failed!")
        return 1


def cmd_remove(args):
    """Remove an enrolled user"""
    config = get_config()
    db = Database(config.get('database.path'))
    
    username = args.username
    
    if db.remove_user(username):
        print(f"✅ Removed user: {username}")
        return 0
    else:
        print(f"❌ User not found: {username}")
        return 1


def cmd_list(args):
    """List enrolled users"""
    config = get_config()
    db = Database(config.get('database.path'))
    
    users = db.get_all_users()
    
    if not users:
        print("No enrolled users found.")
        return 0
    
    print(f"\n{'='*60}")
    print(f"Enrolled Users ({len(users)})")
    print(f"{'='*60}\n")
    
    for user in users:
        last_seen = user.last_seen.strftime('%Y-%m-%d %H:%M:%S') if user.last_seen else 'Never'
        enrolled = user.enrolled_at.strftime('%Y-%m-%d %H:%M:%S')
        
        print(f"👤 {user.username}")
        print(f"   Enrolled: {enrolled}")
        print(f"   Last seen: {last_seen}")
        print()
    
    return 0


def cmd_test(args):
    """Test face authentication"""
    config = get_config()
    config.ensure_directories()
    
    db = Database(config.get('database.path'))
    authenticator = FaceAuthenticator(db)
    
    print(f"\n{'='*60}")
    print(f"Face Authentication - Test")
    print(f"{'='*60}\n")
    print("Please look at the camera...\n")
    
    success, username, confidence = authenticator.authenticate(
        timeout=args.timeout,
        show_preview=not args.no_preview
    )
    
    if success:
        print(f"\n✅ Authentication successful!")
        print(f"   User: {username}")
        print(f"   Confidence: {confidence:.2%}\n")
        return 0
    else:
        print(f"\n❌ Authentication failed!\n")
        return 1


def cmd_start_monitor(args):
    """Start monitoring daemon"""
    script_path = Path(__file__).parent / "monitor_daemon.py"
    
    if args.foreground:
        # Run in foreground
        subprocess.run([sys.executable, str(script_path)])
    else:
        # Run in background
        subprocess.Popen(
            [sys.executable, str(script_path)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )
        print("✅ Monitoring daemon started in background")
    
    return 0


def cmd_stop_monitor(args):
    """Stop monitoring daemon"""
    try:
        result = subprocess.run(
            ['pkill', '-f', 'monitor_daemon.py'],
            capture_output=True
        )
        
        if result.returncode == 0:
            print("✅ Monitoring daemon stopped")
            return 0
        else:
            print("❌ No monitoring daemon found")
            return 1
            
    except Exception as e:
        print(f"❌ Error stopping daemon: {e}")
        return 1


def cmd_status(args):
    """Show system status"""
    config = get_config()
    db = Database(config.get('database.path'))
    
    # Check if daemon is running
    result = subprocess.run(
        ['pgrep', '-f', 'monitor_daemon.py'],
        capture_output=True
    )
    daemon_running = result.returncode == 0
    
    # Get user count
    users = db.get_all_users()
    
    print(f"\n{'='*60}")
    print(f"Face Authentication System - Status")
    print(f"{'='*60}\n")
    
    print(f"Monitoring daemon: {'🟢 Running' if daemon_running else '🔴 Stopped'}")
    print(f"Enrolled users: {len(users)}")
    print(f"Database: {config.get('database.path')}")
    print(f"Config file: {config.config_path}")
    print()
    
    return 0


def cmd_config(args):
    """View or edit configuration"""
    config = get_config()
    
    if args.edit:
        # Open config in editor
        editor = os.getenv('EDITOR', 'nano')
        subprocess.run([editor, str(config.config_path)])
        reload_config()
        print("✅ Configuration updated")
        return 0
    
    elif args.set:
        # Set a config value
        key, value = args.set.split('=', 1)
        
        # Try to parse value
        try:
            if value.lower() == 'true':
                value = True
            elif value.lower() == 'false':
                value = False
            elif value.isdigit():
                value = int(value)
            elif value.replace('.', '', 1).isdigit():
                value = float(value)
        except:
            pass
        
        config.set(key, value)
        config.save()
        print(f"✅ Set {key} = {value}")
        return 0
    
    elif args.get:
        # Get a config value
        value = config.get(args.get)
        print(f"{args.get} = {value}")
        return 0
    
    else:
        # Show config file location
        print(f"Configuration file: {config.config_path}")
        print(f"\nUse --edit to edit configuration")
        print(f"Use --set key=value to set a value")
        print(f"Use --get key to get a value")
        return 0


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Face Authentication System for Linux',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Enable verbose output')
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Enroll command
    enroll_parser = subparsers.add_parser('enroll', help='Enroll a new user')
    enroll_parser.add_argument('username', nargs='?', help='Username to enroll')
    enroll_parser.add_argument('-s', '--samples', type=int, default=5,
                              help='Number of face samples (default: 5)')
    enroll_parser.add_argument('--no-preview', action='store_true',
                              help='Disable camera preview')
    enroll_parser.set_defaults(func=cmd_enroll)
    
    # Remove command
    remove_parser = subparsers.add_parser('remove', help='Remove an enrolled user')
    remove_parser.add_argument('username', help='Username to remove')
    remove_parser.set_defaults(func=cmd_remove)
    
    # List command
    list_parser = subparsers.add_parser('list', help='List enrolled users')
    list_parser.set_defaults(func=cmd_list)
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Test face authentication')
    test_parser.add_argument('-t', '--timeout', type=float, default=10.0,
                            help='Authentication timeout in seconds (default: 10)')
    test_parser.add_argument('--no-preview', action='store_true',
                            help='Disable camera preview')
    test_parser.set_defaults(func=cmd_test)
    
    # Start monitor command
    start_parser = subparsers.add_parser('start-monitor', 
                                        help='Start monitoring daemon')
    start_parser.add_argument('-f', '--foreground', action='store_true',
                             help='Run in foreground')
    start_parser.set_defaults(func=cmd_start_monitor)
    
    # Stop monitor command
    stop_parser = subparsers.add_parser('stop-monitor',
                                       help='Stop monitoring daemon')
    stop_parser.set_defaults(func=cmd_stop_monitor)
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show system status')
    status_parser.set_defaults(func=cmd_status)
    
    # Config command
    config_parser = subparsers.add_parser('config', help='View or edit configuration')
    config_parser.add_argument('--edit', action='store_true',
                              help='Edit configuration file')
    config_parser.add_argument('--set', metavar='KEY=VALUE',
                              help='Set configuration value')
    config_parser.add_argument('--get', metavar='KEY',
                              help='Get configuration value')
    config_parser.set_defaults(func=cmd_config)
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Setup logging
    setup_logging(args.verbose)
    
    # Execute command
    try:
        return args.func(args)
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
        return 130
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=args.verbose)
        print(f"\n❌ Error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
