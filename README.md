# WebProxy-Server-Caching

Development Environment: Python (2.7.9)


Instructions for how to run the program:

1.	Create folder "cache" at the same level at which "Web_Proxy_Server_Caching.py" file located
2.	Create folder "log" at the same level at which "Web_Proxy_Server_Caching.py" file located
3.	Open command prompt
4.	Go to the location where "Web_Proxy_Server_Caching.py" file located
5.	Run command "python Web_Proxy_Server_Caching.py"
6.	Open Firefox browser
7.	Go to Option -> Privacy -> "clear your recent history" -> Clean "Cache"
8.	Copy URL "http://localhost:8080/www.yahoo.com" to browser and hit enter
9.	You will be redirected to the www.yahoo.com through the proxy server.
10.	Log will be generated at '../../log/log.txt'
11.	Cache for yahoo.com will be generated at ‘../../cache/www.yahoo.com'
