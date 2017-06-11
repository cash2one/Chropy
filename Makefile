update: fetch.txt
	mkdir -p proto
	cd proto && xargs -i wget '{}' < ../fetch.txt 

all: update

