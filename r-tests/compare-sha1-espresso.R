library(data.table)
library(boot)

replicates = 1000 # TODO
f1 = 'sha1-32bit-out8bitREF.csv'
f2 = 'sha1-32bit-out8bitREF-espresso.csv'

raw_data1 = read.csv(f1)
raw_data2 = read.csv(f2)
# Columns
#  - rounds     number of rounds
#  - time       time to solve

get_groupped <- function(raw_data) {
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
  return(groupped)
}

groupped_1 = get_groupped(raw_data1)
groupped_2 = get_groupped(raw_data2)

plot(x = 1,
     #log = "y",
     xlim = range(groupped_1$rounds),
     ylim = range(groupped_1$ci_low, groupped_1$ci_high, groupped_2$ci_low, groupped_2$ci_high),
     xlab = "Number of rounds",
     ylab = "Time [seconds]",
     main = paste("Solving time vs. #rounds", sep=""),
     type = "n",
     xaxt = "n")
axis(side = 1,
     at = groupped_1$rounds)

polygon(x = c(groupped_1$rounds, rev(groupped_1$rounds)),
        y = c(groupped_1$ci_low, rev(groupped_1$ci_high)),
        col = "grey",
       border = NA)
lines(groupped_1$rounds, groupped_1$ci_low, type="l", lty=2)
lines(groupped_1$rounds, groupped_1$ci_high, type="l", lty=2)

polygon(x = c(groupped_2$rounds, rev(groupped_2$rounds)),
        y = c(groupped_2$ci_low, rev(groupped_2$ci_high)),
        col = rgb(1, 0.5, 0.5, 0.5),
        border = NA)
lines(groupped_2$rounds, groupped_2$ci_low, type="l", lty=2, col="red")
lines(groupped_2$rounds, groupped_2$ci_high, type="l", lty=2, col="red")

lines(groupped_1$rounds, groupped_1$mean, type="o", pch=20, bg="black")
lines(groupped_2$rounds, groupped_2$mean, type="o", pch=20, bg="black", col="red")