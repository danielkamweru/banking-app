#!/bin/bash
fuser -k 8000/tcp 2>/dev/null
uvicorn app.main:app --reload --port 8000
