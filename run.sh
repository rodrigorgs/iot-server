#!/bin/bash

source venv/bin/activate
venv/bin/flask --app=main.py run --host=0.0.0.0 --port=9091