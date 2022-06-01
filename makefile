install:
	python install -r requirements.txt

run:
	python compiler.py

test:
	python3 compiler.py && ./tester

debug:
	python3 compiler.py && ./tester -d

permit:
	chmod +x tester