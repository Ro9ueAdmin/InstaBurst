# Date: 12/14/2017
# Author: Ethical-H4CK3R
# Description: Controls Bruteforce Objects

from constants import colors
from threading import Thread

class Regulate(object):

 def __init__(self, obj):
  self.obj = obj

 @property
 def info(self):
  attempts = '{}{}{}'.format(colors['yellow'], self.obj.attempts, colors['white'])
  wordlist = '{}{}{}'.format(colors['blue'], self.obj.wordlist, colors['white'])
  ip = '{}{}{}'.format(colors['blue'] if self.obj.ip else colors['white'],
                       self.obj.ip if self.obj.ip else '', colors['white'])
  pwd = '{}'.format(self.obj.pwd if self.obj.pwd else '')

  return '\n[-] Proxy-IP: {}\n[-] Wordlist: {}\n[-] Username: {}\
  \n[-] Password: {}\n[-] Attempts: {}\n'.format(ip, wordlist,
  self.obj.username, pwd, attempts)

 @property
 def simple_info(self):
  return self.obj.username.title(), self.obj.wordlist

 def start(self):
  if self.obj.is_alive:return
  Thread(target=self.obj.run).start()

 def reset(self):
  self.stop()
  self.obj.msg = None
  self.obj.attempts = 0
  self.obj.passlist.queue = []
  self.obj.session_write()

 def stop(self):
  self.obj.kill()

 def remove(self):
  self.stop()
  self.obj.session.remove()
