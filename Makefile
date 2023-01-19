install:
	poetry update

clean:
	rm -rf build dist

build: clean
	poetry check
	poetry build

deploy: build
	poetry publish --repository dolead
	git tag $(shell poetry version -s)
	git push --tags
