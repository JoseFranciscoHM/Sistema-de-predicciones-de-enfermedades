"""
PythonAnywhere ASGI entry point.
Configure in PythonAnywhere Web tab:
  - ASGI app: wsgi.application
  - Working directory: /home/<user>/SDD
  - Virtualenv: /home/<user>/.virtualenvs/sdd
  - Static files: /static/ -> /home/<user>/SDD/static/
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from app import app

application = app
