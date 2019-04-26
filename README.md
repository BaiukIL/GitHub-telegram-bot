This telegram bot collects info about most stared GitHub repositories' languages and makes up statistic based on search.
Currently it maintains next commands:

/start		- greeting

/help		- show help

/getstatistic	- show current statistic

 inline:
 
send statistic 	- send current statistic in conversation

Note: /getstatistic and inline 'send statistic' work pretty long (about 20 sec)('send statistic' doesn't work at all this case) when called first time or when it's passed more than minute since previous call. It works this way unless multiprocesses are implanted.
