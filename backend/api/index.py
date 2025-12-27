# Vercel Serverless Function entry point
# This file is used by Vercel to handle API requests

from app import app

# Vercel expects a handler function
def handler(request):
    return app(request.environ, lambda status, headers: None)

# For Vercel Python runtime
app = app

