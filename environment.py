import getpass
import os
import socket

username = getpass.getuser()
print(username)

homedir = os.environ['HOME']  # type: object
print(homedir)

hostname = socket.gethostname()
print(hostname)

fqdn = socket.getfqdn() 
print(fqdn)


