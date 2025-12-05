#!/bin/bash
set -e  # Exit script on first error


echo "✅ Starting Flask application..."
exec gunicorn -w 4 -b 0.0.0.0:$PORT run:app
#!/bin/sh
gunicorn --workers=4 --threads=2 run:app
