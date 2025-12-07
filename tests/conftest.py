"""
Pytest configuration and shared fixtures
"""

import pytest
import tempfile
import shutil
from pathlib import Path
import sys
import os
import numpy as np
from unittest.mock import MagicMock, Mock

# Mock problematic imports BEFORE they are imported by other modules
sys.modules['face_recognition'] = MagicMock()
sys.modules['cv2'] = MagicMock()
sys.modules['dbus'] = MagicMock()
sys.modules['dbus.service'] = MagicMock()
sys.modules['dbus.mainloop.glib'] = MagicMock()

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests"""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    shutil.rmtree(temp_path)


@pytest.fixture
def test_config_dir(temp_dir):
    """Create a test configuration directory"""
    config_dir = temp_dir / "config"
    config_dir.mkdir(parents=True)
    return config_dir


@pytest.fixture
def test_data_dir(temp_dir):
    """Create a test data directory"""
    data_dir = temp_dir / "data"
    data_dir.mkdir(parents=True)
    return data_dir


@pytest.fixture
def test_config_file(test_config_dir):
    """Create a test configuration file"""
    config_path = test_config_dir / "config.yaml"
    config_content = """
camera:
  device_id: 0
  width: 640
  height: 480

recognition:
  tolerance: 0.6
  model: "hog"
  num_jitters: 1
  
enrollment:
  num_samples: 3
  sample_delay: 0.5
  min_face_size: 50

monitoring:
  enabled: true
  check_interval: 2.0
  absence_timeout: 10.0
  presence_confirmation_time: 3.0

database:
  path: "{data_dir}/test_face_auth.db"

logging:
  level: "DEBUG"
  file: "{data_dir}/test_face_auth.log"

actions:
  on_absence:
    - log
  on_presence:
    - log
  on_auth_success:
    - log
  on_auth_failure:
    - log

hooks:
  on_presence: []
  on_absence: []
  on_auth_success: []
  on_auth_failure: []
"""
    config_path.write_text(config_content)
    return config_path


@pytest.fixture
def mock_face_encoding():
    """Generate a mock face encoding"""
    return np.random.rand(128).astype(np.float64)


@pytest.fixture
def mock_face_image():
    """Generate a mock face image (BGR format)"""
    # Create a simple 480x640x3 image
    image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    return image


@pytest.fixture
def mock_face_location():
    """Generate a mock face location"""
    # (top, right, bottom, left)
    return (100, 400, 300, 200)


@pytest.fixture(autouse=True)
def reset_environment():
    """Reset environment variables before each test"""
    # Store original environment
    original_env = os.environ.copy()
    
    yield
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)
