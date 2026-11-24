.PHONY: default clean

default: paper.pdf

paper.pdf: $(wildcard *.tex *.bib figures/*)
	latexmk -pdf $<

clean:
	latexmk -C
