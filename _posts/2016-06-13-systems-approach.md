---
title: "A systems approach"
categories:
    - Design Decisions
tags:
    - Systems
    - Top-level design
published: false
---

## Motivation

I wanted the Desk Defender to be a *system* rather than just a machine. This would serve two purposes.

Firstly, it would allow the design to be broken down into smaller goals. This should help with motivation during what I expect will be a long project. If I get frustrated with one aspect of the design, or need to change the approach, other elements of the system could remain both intact and also allow me to keep making progress. This would likely happen anyway, since I will be working on hardware design, electronics and software, but breaking the project down at a higher level seemed like a good idea.

The second purpose of a systems approach is for its educational value. Engineering is built on systems, and this project should attempt to show how that is achieved. Having discrete systems to talk about makes this job eaiser: I could talk about the image processing system in isolation to people interested in software, and then explain that the output is supplied to a separate system. I also thought that I could provide alternative systems that serve the same purpose. For example, I could have an automatic target designator -- a gimbal-mounted laser -- that is fed by image processing. But I could also give someone a laser pen and ask them to point it at the target. The rest of the system would be able to work regardless of how the laser spot is produced.

## A decoupled system

My original idea was to use a camera to detect and track a moving target. This was largely based on a [post](http://www.pyimagesearch.com/2015/06/01/home-surveillance-and-motion-detection-with-the-raspberry-pi-python-and-opencv/) I found on [PyImageSearch](http://www.pyimagesearch.com/). The software could output steering commands to a turret-mounted gun which could then point in (hopefully) the right direction and fire.

The original idea should work within the same constraints and limitations of this entire project. But I decided to decouple the concept into several systems:

* Acquisition system
* Automatic target designation system
* Manual target designator
* Target tracking system
* Gun turret
* Manual turret control system
* Gun
* Ammunition feed system
* Kill switch
* Power supply
* Logging/diagnostics

