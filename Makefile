default:
	venv/bin/python3 import.py

install:
	python3 -m venv venv
	venv/bin/pip3 install -r requirements.txt