# Radio Log Liberator
Liberate your radio logs from qrz.com with the power of Python. Logliberator is a simple Python script that scrapes your data and outputs an .adf file for logbook importing. This .adf can then be further imported/exported into various other software.

## Caveats
This is really a simple hack of a script. There is a considerable room for improvement and users should use it at their own risk. I intend to keep working on this script and encourage feedback from the community. 
The script was developed and tested on Linux using Python. There are many things that I would like to improve in the future. At this point, I just wanted a simple way to export my contacts and I think there are others that want the same. 

The following modules are required:  
  * [Requests](http://docs.python-requests.org/en/latest/)
  * [BeautifulSoup](http://www.crummy.com/software/BeautifulSoup/)
    
## Getting Started
Once you have download the script, simply run it with python logliberator.py. The user will need to input their username and password from qrz.com. The script will output 'Logbook.adi' into the directory the script is executed in.  

## Miscellaneous
If you find this script useful, please drop me a line and let me know that it worked for you. I frequent the [/r/amateurradio](https://www.reddit.com/r/amateurradio/) subreddit and can sometimes be found there. If you are having problems, feel free to contact me and I will do my best to help you out. I am currently an American living out of the country though, so it may take me a few days to respond.


## Contributing
Making improvements is encouraged. If you just have an idea or comment, I welcome those as well. This script is released for the amateur radio community as a whole, if you find it useful drop me a message and let me know. I encourage anyone to contact me at shawnjones20@gmail.com if you have any questions. 

