# Date: 11/27/2017
# Author: Ethical-H4CK3R
# Description: Browser

from time import time
from commands import getoutput as shell
from requests import Session, get as urlopen
from constants import ip_fetch_timeout, site_details, network_manager_time

class Spyder(object):
 def __init__(self):
  self.last_restarted = None # the last time network manager was restarted

 @property
 def br(self):
  session = Session()
  session.headers.update(site_details['header'])
  return session 

 def restart_net_manager(self):
  shell('service network-manager restart')

 @property
 def ip_addr(self):
  try:
   ip = str(urlopen('https://api.ipify.org/?format=text', timeout=ip_fetch_timeout).text)
   self.last_restarted = None
   return ip
  except:
   if not self.last_restarted:
    self.last_restarted = time()
    self.restart_net_manager()
   else:
    if time() - self.last_restarted >= network_manager_time:
     self.last_restarted = time()
     self.restart_net_manager()
