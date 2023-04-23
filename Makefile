default:
	venv/bin/python3 import.py

require:
	venv/bin/pip3 install $(pack)

freeze:
	venv/bin/python3 -m pip freeze > requirements.txt

install:
	python3 -m venv venv
	venv/bin/pip3 install -r requirements.txt