library(data.table)
library(Rssa)
library(lattice)
#t.start <- as.Date("2010-01-01")
#t.end <- as.Date("2017-07-23")
#
#bt.date <- seq.Date(t.start, t.end, 1)
#
#n <- length(bt.date)
#T <- 1:n
#
#dt <- data.table(date=bt.date)
#dt[,year:=year(date)]
#dt[,nb.day.year:=sum(sign(year)), by=year]

period <- 260
n <- 5
a <- 1/period

T <- seq(1,(n*period))

x <- sin(2*pi*T/period) + rnorm(n*period, sd=0.5)
#x <- a*T + sin(2*pi*T/period) + 0.5*cos(pi*T/period) +  rnorm(n*period, sd=0.5)
#X11()
#plot(T, x, type='l')


dec <- ssa(x)

rec <- reconstruct(dec,
	groups=list(one=c(1,2)))


plot(T, x, type='l',col='grey')

lines(T, rec$one, col='green', lwd=2)


## plot(T, x - rec$one - rec$two, col='blue', lwd=2)

#lines(T, rec$one + rec$two + rec$three, col='orange', lwd=2)
#lines(T, rec$one + rec$two + rec$three + rec$res, col='red', lwd=2)
