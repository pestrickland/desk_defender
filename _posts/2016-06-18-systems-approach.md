---
title: "A systems approach"
categories:
    - Design Decisions
tags:
    - Systems
    - Top-level design
published: true
excerpt: "An overview of the different systems I intend to design."
modified: 2016-06-19
---

## Motivation

I want the Desk Defender to be a clear example of a *system* rather than just a machine. This would serve two purposes.

Firstly, it would allow the design to be broken down into smaller goals. This should help with motivation during what I expect will be a long project. If I get frustrated with one aspect of the design, or need to change the approach, other elements of the system could remain both intact and also allow me to keep making progress. This would likely happen anyway, since I will be working on hardware design, electronics and software, but breaking the project down at a higher level seems like a good idea.

The second purpose of a systems approach is for its educational value. Engineering is built on systems, and this project should attempt to show how that is achieved. Having discrete systems to talk about makes this job eaiser: I could talk about the image processing system in isolation to people interested in software, and then explain that the output is supplied to a separate system. I also thought that I could provide alternative systems that serve the same purpose. For example, I could have an automatic target designator -- a gimbal-mounted laser -- that is fed by image processing. But I could also give someone a laser pen and ask them to point it at the target. The rest of the system would be able to work regardless of how the laser spot is produced.

## A decoupled system

My original idea was to use a camera to detect and track a moving target. This was largely based on a [post](http://www.pyimagesearch.com/2015/06/01/home-surveillance-and-motion-detection-with-the-raspberry-pi-python-and-opencv/) I found on [PyImageSearch](http://www.pyimagesearch.com/). The software could output steering commands to a turret-mounted gun which could then point in (hopefully) the right direction and fire.

The original idea should work within the same constraints and limitations of the project, but I decided to decouple the concept into several systems:

* Acquisition
* Designation
* Tracking
* Gun
* Power supply
* Safety

![System outline]({{ site.url }}{{ site.baseurl }}/images/system_outline.svg)

As shown above, the designation and tracking systems have manual alternatives.

### Acquisition

The acquisition system is anticipated to be a video camera and image processing system. Raspberry Pi-based, it should detect moving images and output coordinates or possibly a vector.

Not visible on the diagram is the manual equivalent to the acquisition system, the Mk 1 Eyeball...

### Designation

The output from the acquisition system should generate steering commands for a designator. The automatic system will be a low power laser diode, probably simply mounted on a 2-axis gimbal powered by servos. The difficulty will be converting pixel-based coordinates to angles for the servo motors. I may need to design a calibration function to map the field of view of the camera with the arcs of motion for the servos.

As discussed above, a manual alternative is a laser pointer, and a volunteer could be given the opportunity to try pointing at the target by eye.

### Tracking

Rather than taking the acquisition system's output directly, the tracking system will look for a laser spot. Another Raspberry Pi-based system, it will steer the gun towards the detected laser spot.

The manual system will directly control the gun turret. I could probably do this in one of three ways:

1. Design a hand controller
2. Use a radio control transmitter
3. Use the buttons on the [BBC micro:bit](https://www.microbit.co.uk/) to control the gun

I like the last point the best. Every school pupil is supposed to be given a micro:bit, so to be able to provide some code and a means to control the gun with that could be quite interesting.

### Gun

The original system I started work on was the gun. I initially envisaged a minigun-type design, but currently think a single-barrel gun will be the easiest.

### Power supply

Describing the power supply as a system is perhaps overkill, but it might still be beneficial to think of it in that way.

### Safety

Originally I discounted safety as being a separate system because I wanted it to be integrated throughout the design. However, the point of system safety is to make the *entire* system safe, and to do this there needs to be an interface between each of the safety aspects. With that in mind, I decided that it would be a separate system that interfaces with everything else.
