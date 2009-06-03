import sys
sys.path.append('./google_appengine')
sys.path.append('./google_appengine/lib')
sys.path.append('./google_appengine/lib/webob') 

from waveapi import events
from waveapi import model
from waveapi import robot

print 'Content-Type: text/plain'
print ''
print 'Hello, world!'