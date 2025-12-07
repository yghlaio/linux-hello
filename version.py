"""
Linux Hello - Face Authentication for Linux
Version information
"""

__version__ = "1.0.0"
__author__ = "Rex Ackermann"
__description__ = "Windows Hello™-style facial authentication for Linux"
__project_name__ = "Linux Hello"

# Feature flags
FEATURES = {
    'gui': True,
    'pam': True,
    'bash_integration': True,
    'monitoring': True,
    'event_hooks': True,
    'dbus': True,
    'security_modes': True,
    'sample_management': True,
}

# Known limitations
LIMITATIONS = [
    "Not as secure as password authentication",
    "Requires good lighting conditions",
    "Performance varies by hardware",
    "Rotation invariance in development",
]

def get_version_info():
    """Get formatted version information"""
    return f"""
Face Authentication System v{__version__}
{__description__}

Features:
""" + "\n".join(f"  - {k}: {'✓' if v else '✗'}" for k, v in FEATURES.items()) + f"""

Limitations:
""" + "\n".join(f"  - {l}" for l in LIMITATIONS)
