filename=main
fullname=${filename}.tex
default: pdf
pdf:
	pdflatex ${fullname}
	bibtex ${filename}
	pdflatex ${fullname}
	bibtex ${filename}
	pdflatex ${fullname}
clean:
	rm -f ${filename}.pdf
	rm -f ${filename}.aux
	rm -f ${filename}.bbl
	rm -f ${filename}.blg
	rm -f ${filename}.log
	rm -f ${filename}.out
	rm -f ${filename}.cicmauthinsts
