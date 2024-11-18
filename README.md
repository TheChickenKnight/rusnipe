# rusnipe
my Rutgers class sniper
this is a WIP, I feel like an archaeologist finding ancient ruins

# What I know so far:
## API endpoint
The SOC is so terribly documented so the only place i found hint of the api was on [this github page](https://github.com/rpatel3001/RU-Interested/). Thank you.
[classes.rutgers.edu/soc/courses.gz?term=1&year=2025&campus=NB](https://classes.rutgers.edu/soc/courses.gz?term=1&year=2025&campus=NB)
## Parameters
These are the only parameters I was able to find. There isn't one called "subject", but I'm really hoping to find more to be able to narrow down the file however not needed.
### Term
*int 1-4*
The given term in year. goes Spring, Summer, Fall, Winter from 1 to 4.
### Year
*int*
The year of classes
### Campus
*String*
I only care about New Brunswick so we're using "NB"
## Format
The api returns a compressed .gz containing a no extension file which is a JSON.
I will use pako[![NPM version](https://img.shields.io/npm/v/pako.svg)](https://www.npmjs.org/package/pako) to decompress the file.
