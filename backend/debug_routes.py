import sys
import os

# Add backend directory to sys.path
sys.path.append(os.getcwd())

from app.main import app

for route in app.routes:
    methods = getattr(route, 'methods', None)
    path = getattr(route, 'path', None)
    name = getattr(route, 'name', None)
    print(f"{methods} {path} [{name}]")
