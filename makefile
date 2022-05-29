install:
	python install -r requirements.txt

run:
	python compiler.py

test:
	python3 compiler.py && ./tester

permit:
	chmod +x tester