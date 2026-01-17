#!/bin/bash
cd /home/user/Development/code/fullstack/Banking-App
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}