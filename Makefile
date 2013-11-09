update:
	python dl.py
	git commit -m "periodic data update `date`" data

.PHONY: update
