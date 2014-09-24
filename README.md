Description
===========
Raspi-sump is a sump pit water level monitoring system using a Raspberry Pi and an 
Ultrasonic Sensor (HC-SR04)

Currently the system monitors the water level in your pit at defined intervals. It sends
email sms alerts if the water reaches a critical level, indicating a possible sump pump failure.

The Raspberry Pi uses Linux (Raspbian) which is not a real time OS.  This has implications 
for this type of application as a multitasking OS like Linux will cause some small error
variance in the readings, as opposed to an Arduino that uses a RealTime OS. 

While the accuracy is fine for a home system, the problem is mitigated by taking a larger sorted sample of readings and using the median reading as the reported one.  In my testing so far I have a variance of about one centimeter which is acceptable for a residential monitoring system.  It would appear that using the median reading eliminates the infrequent fringe type readings that can give false positives.

Future versions will include;
- An offsite web component for viewing historical data, including graphs and water volume
- Proper push button shutdown to turn off the pi (raspi-atx)
- LCD panel to get a quick glance of the water level without opening the lid.

More Info
=========
Further details provided at http://www.linuxnorth.org/raspi-sump/

An hourly updating graph is available for view.
http://www.linuxnorth.org/raspi-sump/raspi-sump-today.html

Disclaimer
==========
Raspi-Sump is still experimental software. You are welcome to use it but there is no guarantee it will work. Your house may still flood if your sump pump fails. Use for experimental purposes only.

This is not a replacement for remaining vigilant in maintaining your water pumping system. It is one tool you can use to give yourself extra piece-of-mind.

Best practices should also include:

- A backup pump that triggers at a slightly higher water level than your main pump.
- The secondary pump should be connected to a seperate dedicated electrical breaker. 
- You should also have a generator that can provide power should you have an extended outage during the spring or other unseasonally wet time of year.
- if you are building a new home, pay attention to the grade of your property, as you may even be able to let gravity empty your pit for you.  That would be the best approach with a backup pump just in case. 

Once you have done all of these things, then consider using a monitoring system like Raspi-Sump.

License
=======
I added a license for the main purpose of the use AS-IS clause in case you use this and your basement floods or causes any other disaster.  You agree that your use of Raspi-Sump is at your own risk. 
