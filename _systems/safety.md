---
title: "Safety System"
---

*Is this a system?*

Various aspects for safety need to be considered:

* Kill switch, to enable the system to be instantly stopped on command
* Fail safe in all aspects, so that the system defaults to safe
* Interlocks, to ensure that risk to people is mitigated

The kill switch could be a system of its own. Sparkfun has a tutorial for a wireless system that uses a low power radio to transmit from the controller to the system (a robot in this case). In the event of the switch being thrown, or the signal being lost, the system is turned off. For my application I could make use of this idea in its entirety. I could even get some audience participation by handing out a wireless box to someone.

In terms of interlocks, I'm currently only thinking of something like a laser beam barrier. Setting up a type of arena, lasers could be used on the boundaries, and in the event that someone crossed them, the system would be made safe. That should be fairly simple to implement.

The more I think about it, the more the safety features of the system might warrant their own subsystem, if only to connect all the inputs into a single isolator switch or something. It could also just be a feature of the power supply and distribution system, but a discrete system might be better.