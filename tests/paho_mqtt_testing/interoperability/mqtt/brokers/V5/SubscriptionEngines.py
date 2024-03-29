"""
*******************************************************************
  Copyright (c) 2013, 2018 IBM Corp.

  All rights reserved. This program and the accompanying materials
  are made available under the terms of the Eclipse Public License v1.0
  and Eclipse Distribution License v1.0 which accompany this distribution.

  The Eclipse Public License is available at
     http://www.eclipse.org/legal/epl-v10.html
  and the Eclipse Distribution License is available at
    http://www.eclipse.org/org/documents/edl-v10.php.

  Contributors:
     Ian Craggs - initial implementation and/or documentation
*******************************************************************
"""

from . import Topics, Subscriptions
import mqtt.formats.MQTTV5 as MQTTV5

from .Subscriptions import *

logger = logging.getLogger('MQTT broker')

def isDollarTopic(name):
  return name[0] == '$' and not name.startswith('$share/')

class SubscriptionEngines:

   def __init__(self, sharedData={}):
     self.sharedData = sharedData
     if "subscriptions" not in self.sharedData:
       self.sharedData["subscriptions"] = []  # list of subscriptions
     else:
       logger.info("Sharing subscription data")
     if "dollar_subscriptions" not in self.sharedData:
       self.sharedData["dollar_subscriptions"] = []  # list of subscriptions
     self.__subscriptions = self.sharedData["subscriptions"] 
     self.__dollar_subscriptions = self.sharedData["dollar_subscriptions"] 
     if "retained" not in self.sharedData:
       self.sharedData["retained"] = {}  # map of topics to retained msg+qos
     self.__retained = self.sharedData["retained"]
     if "dollar_retained" not in self.sharedData:
       self.sharedData["dollar_retained"] = {}  # map of topics to retained msg+qos
     self.__dollar_retained = self.sharedData["dollar_retained"] 

   def reinitialize(self):
     self.__init__()

   def subscribe(self, aClientid, topic, options):
     if type(topic) == type([]):
       rc = []
       count = 0
       for aTopic in topic:
         rc.append(self.__subscribe(aClientid, aTopic, options[count]))
         count += 1
       if count > 1:
         logger.info("[MQTT-3.8.4-4] Multiple topics in one subscribe")
     else:
       rc = self.__subscribe(aClientid, topic, options)
     return rc

   def __subscribe(self, aClientid, aTopic, options):
     "subscribe to one topic"
     rc = None
     resubscribed = False
     if Topics.isValidTopicName(aTopic):
       subscriptions = self.__subscriptions if not isDollarTopic(aTopic) else self.__dollar_subscriptions
       for s in subscriptions:
         if s.getClientid() == aClientid and s.getTopic() == aTopic:
           s.resubscribe(options)
           resubscribed = True
       if not resubscribed:
         rc = Subscriptions(aClientid, aTopic, options)
         subscriptions.append(rc)
     return rc, resubscribed

   def unsubscribe(self, aClientid, aTopic):
     rc = []
     matchedAny = False
     if type(aTopic) == type([]):
       if len(aTopic) > 1:
         logger.info("[MQTT-3.10.4-6] each topic must be processed in sequence")
       for t in aTopic:
         matched = self.__unsubscribe(aClientid, t)
         rc.append(MQTTV5.ReasonCodes(MQTTV5.PacketTypes.UNSUBACK, "Success") if matched else
                   MQTTV5.ReasonCodes(MQTTV5.PacketTypes.UNSUBACK, "No subscription found"))
         if not matchedAny:
           matchedAny = matched
     else:
       matchedAny = self.__unsubscribe(aClientid, aTopic)
       rc.append(ReasonCodes(UNSUBACK, "Success") if matched else ReasonCodes(UNSUBACK, "No subscription found"))
     if not matchedAny:
       logger.info("[MQTT-3.10.4-5] Unsuback must be sent even if no topics are matched")
     return rc

   def __unsubscribe(self, aClientid, aTopic):
     "unsubscribe to one topic"
     matched = False
     if Topics.isValidTopicName(aTopic):
       subscriptions = self.__subscriptions if not isDollarTopic(aTopic) else self.__dollar_subscriptions
       for s in subscriptions:
         if s.getClientid() == aClientid and s.getTopic() == aTopic:
           logger.info("[MQTT-3.10.4-1] topic filters must be compared byte for byte")
           logger.info("[MQTT-3.10.4-2] no more messages must be added after unsubscribe is complete")
           subscriptions.remove(s)
           matched = True
           break # once we've hit one, that's us done
     return matched

   def clearSubscriptions(self, aClientid):
     for subscriptions in [self.__subscriptions, self.__dollar_subscriptions]:
       for s in subscriptions[:]:
         if s.getClientid() == aClientid:
           subscriptions.remove(s)

   def getSubscriptions(self, aTopic, aClientid=None):
     "return a list of subscriptions for this client"
     rc = None
     if Topics.isValidTopicName(aTopic):
       subscriptions = self.__subscriptions if not isDollarTopic(aTopic) else self.__dollar_subscriptions
       if aClientid == None:
         rc = [sub for sub in subscriptions if Topics.topicMatches(sub.getTopic(), aTopic)]
       else:
         rc = [sub for sub in subscriptions if sub.getClientid() == aClientid and Topics.topicMatches(sub.getTopic(), aTopic)]
     return rc

   def optionsOf(self, clientid, topic):
     # if there are overlapping subscriptions, choose maximum QoS
     chosen = None
     for sub in self.getSubscriptions(topic, clientid):
       if chosen == None:
         if hasattr(sub, "getOptions"):
           chosen = sub.getOptions()
         else: # MQTT V3 case
           chosen = (MQTTV5.SubscribeOptions(QoS=sub.getQoS()), MQTTV5.Properties(MQTTV5.PacketTypes.SUBSCRIBE))
       else:
         logger.info("[MQTT-3.3.5-1] Overlapping subscriptions max QoS")
         if sub.getQoS() > chosen[0].QoS:
           if hasattr(sub, "getOptions"):
             chosen = sub.getOptions()
           else: # MQTT V3 case
             chosen = (MQTTV5.SubscribeOptions(QoS=sub.getQoS()), MQTTV5.Properties(MQTTV5.PacketTypes.SUBSCRIBE))
       # Omit the following optimization because we want to check for condition [MQTT-3.3.5-1]
       #if chosen == 2:
       #  break
     return chosen

   def subscriptions(self, aTopic):
     "list all clients subscribed to this (non-wildcard) topic"
     result = set()
     if Topics.isValidTopicName(aTopic):
       subscriptions = self.__subscriptions if not isDollarTopic(aTopic) else self.__dollar_subscriptions
       for s in subscriptions:
         if Topics.topicMatches(s.getTopic(), aTopic):
           result.add(s) # don't add a subscription twice
     return result

   def setRetained(self, aTopic, aMessage, aQoS, receivedTime, properties):
     "set a retained message on a non-wildcard topic"
     if Topics.isValidTopicName(aTopic):
       retained = self.__retained if not isDollarTopic(aTopic) else self.__dollar_retained
       if len(aMessage) == 0:
         if aTopic in retained.keys():
           logger.info("[MQTT-3.3.1-11] Deleting zero byte retained message")
           del retained[aTopic]
       else:
         retained[aTopic] = (aMessage, aQoS, receivedTime, properties)

   def getRetained(self, aTopic):
     "returns (msg, QoS, properties) for a topic"
     result = None
     if Topics.isValidTopicName(aTopic):
       retained = self.__retained if not isDollarTopic(aTopic) else self.__dollar_retained
       if aTopic in retained.keys():
         result = retained[aTopic]
     return result

   def getRetainedTopics(self, aTopic):
     "returns a list of topics for which retained publications exist"
     if Topics.isValidTopicName(aTopic):
       retained = self.__retained if not isDollarTopic(aTopic) else self.__dollar_retained
       return retained.keys()
     else:
       return None


def unit_tests():
  se = SubscriptionEngines()
  se.subscribe("Client1", ["topic1", "topic2"], [2, 1])
  assert se.subscribers("topic1") == ["Client1"]
  se.subscribe("Client2", ["topic2", "topic3"], [2, 2])
  assert se.subscribers("topic1") == ["Client1"]
  assert se.subscribers("topic2") == ["Client1", "Client2"]
  se.subscribe("Client2", ["#"], [2])
  assert se.subscribers("topic1") == ["Client1", "Client2"]
  assert se.subscribers("topic2") == ["Client1", "Client2"]
  assert se.subscribers("topic3") == ["Client2"]
  assert set(map(lambda s:s.getTopic(), se.getSubscriptions("Client2"))) == set(["#", "topic2", "topic3"])
  logger.info("Before clear: %s", se.getSubscriptions("Client2"))
  se.clearSubscriptions("Client2")
  assert se.getSubscriptions("Client2") == []
  assert se.getSubscriptions("Client1") != []
  logger.info("After clear, client1: %s", se.getSubscriptions("Client1"))
  logger.info("After clear, client2: %s", se.getSubscriptions("Client2"))
