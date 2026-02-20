#!/usr/bin/env bash
# Run the test suite.
# PYTHONPATH=src is required to override any ROS-injected paths that would
# cause the broken launch_pytest entrypoint to be loaded by pytest.
PYTHONPATH=src .venv/bin/python -m pytest tests/ "$@"
