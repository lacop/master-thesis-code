library(data.table)
library(boot)

replicates = 1000 # TODO
#filename = 'sha1-32bit-out12bitREF.csv'
filename = 'sha1-32bit-out8bitREF.csv'


#raw_data = read.csv('sha1-16bit-nores.csv')
raw_data = read.csv(filename)
# Columns
#  - rounds     number of rounds
#  - time       time to solve

tbl = data.table(raw_data)
groupped = tbl[,list(times=list(time)), by=rounds]
groupped = groupped[order(rounds)] # Sort by number of rounds, for plotting

bca_mean <- function(data, indices) {
    filtered_data <- data[indices]
    return(mean(filtered_data))
}

times_stat <- function(times) {
    if (length(unique(times)) > 1) {
        bobj = boot(data=times, statistic=bca_mean, R=replicates)
        ci = boot.ci(bobj, type="bca", conf=0.95)
        return(list(mean=mean(times), ci_low=ci$bca[4], ci_high=ci$bca[5]))
    } else {
        return(list(mean=mean(times), ci_low=mean(times), ci_high=mean(times)))
    }
}

for(r in groupped$rounds) {
    times <- unlist(groupped[groupped$rounds==r]$times)
    #print(r)
    #print(times)
    stat = times_stat(times)
    groupped[groupped$rounds==r, "mean"] = stat$mean
    groupped[groupped$rounds==r, "ci_low"] = stat$ci_low
    groupped[groupped$rounds==r, "ci_high"] = stat$ci_high
}

plot(x = 1,
     #log = "y",
     xlim = range(groupped$rounds),
     ylim = range(groupped$ci_low, groupped$ci_high),
     xlab = "Number of rounds",
     ylab = "Time [seconds]",
     main = paste("Solving time vs. #rounds [", filename, "]", sep=""),
     type = "n",
     xaxt = "n")
axis(side = 1,
     at = groupped$rounds)
polygon(x = c(groupped$rounds, rev(groupped$rounds)),
        y = c(groupped$ci_low, rev(groupped$ci_high)),
        col = "grey",
        border = NA)
lines(groupped$rounds, groupped$ci_low, type="l", lty=2)
lines(groupped$rounds, groupped$ci_high, type="l", lty=2)
lines(groupped$rounds, groupped$mean, type="o", pch=20, bg="black")
