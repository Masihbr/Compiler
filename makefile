install:
	python install -r requirements.txt

run:
	python compiler.py

test:
	python3 compiler.py && ./tester

debug:
	python3 compiler.py && ./tester -d

print:
	make test > test.txt && clear && cat test.txt && rm test.txt

permit:
	chmod +x tester