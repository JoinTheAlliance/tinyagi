import os
import sys
from datetime import datetime
from tinyagi.core.loop import write_observation_to_log, observe
from tinyagi.core.system import get_epoch

def test_write_observation_to_log():
    # Enable debug mode
    os.environ["TINYAGI_DEBUG"] = "true"

    # Generate test data
    observation_data = {
        "epoch": get_epoch(),
        "last_epoch": str(get_epoch() - 1),
        "current_time": datetime.now().strftime("%H:%M"),
        "current_date": datetime.now().strftime("%Y-%m-%d"),
        "platform": sys.platform,
        "cwd": os.getcwd(),
        "events": 'Test Events',
        "recent_knowledge": 'Test Knowledge',
    }

    # Run the function
    write_observation_to_log(observation_data)
    
    # Check that a log file was created
    log_files = os.listdir("./logs/loop")
    assert len(log_files) > 0, 'No log file created'

def test_create_initial_observation():
    epoch = get_epoch()
    # Run the function
    observation_data = observe()

    # Check that keys are present
    assert "epoch" in observation_data, 'Key "epoch" not found'
    # assert the epoch in the observation data is the same as the current epoch
    assert observation_data["epoch"] == epoch, 'Epoch in observation data does not match current epoch'
    assert "last_epoch" in observation_data, 'Key "last_epoch" not found'
    assert observation_data["last_epoch"] == str(epoch - 1), 'Last epoch in observation data does not match current epoch minus 1'
    assert "current_time" in observation_data, 'Key "current_time" not found'
    assert observation_data["current_time"] == datetime.now().strftime("%H:%M"), 'Current time in observation data does not match current time'
    assert "current_date" in observation_data, 'Key "current_date" not found'
    assert observation_data["current_date"] == datetime.now().strftime("%Y-%m-%d"), 'Current date in observation data does not match current date'
    assert "platform" in observation_data, 'Key "platform" not found'
    assert observation_data["platform"] == sys.platform, 'Platform in observation data does not match current platform'
    assert "cwd" in observation_data, 'Key "cwd" not found'
    assert observation_data["cwd"] == os.getcwd(), 'CWD in observation data does not match current CWD'
    # assert "events" in observation_data, 'Key "events" not found'
    # assert "recent_knowledge" in observation_data, 'Key "recent_knowledge" not found'

    # Check that the types of values are correct
    assert isinstance(observation_data["epoch"], int), 'epoch is not an integer'
    assert isinstance(observation_data["last_epoch"], str), 'last_epoch is not a string'
    assert isinstance(observation_data["current_time"], str), 'current_time is not a string'
    assert isinstance(observation_data["current_date"], str), 'current_date is not a string'
    assert isinstance(observation_data["platform"], str), 'platform is not a string'
    assert isinstance(observation_data["cwd"], str), 'cwd is not a string'
    assert isinstance(observation_data["events"], str), 'events is not a string'
    assert isinstance(observation_data["recent_knowledge"], str), 'recent_knowledge is not a string'

def run_tests():
    test_write_observation_to_log()
    test_create_initial_observation()
    print('All tests complete!')
