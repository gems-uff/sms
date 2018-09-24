test:
	py.test --verbose -s
testpdb:
	py.test --verbose -s --pdb
cov:
	py.test --cov-config .coveragerc --cov-report term-missing --cov=app tests/
