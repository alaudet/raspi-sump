Raspi-sump is a sump pit water level monitoring system using a Raspberry Pi and an 
Ultrasonic Sensor (HC-SR04)

Currently the system monitors the water level in your pit at defined intervals. It sends
email sms alerts if the water reaches a critical level, indicating a possible sump pump failure.

The Raspberry Pi uses Linux (Raspbian) which is not a real time OS.  This has implications 
for this type of application as a multitasking OS like Linux will cause some small error
variance in the readings, as opposed to an Arduino that uses a RealTime OS. 

While the accuracy is fine for a home system, the problem is further mitigated by taking a larger sorted sample of readings and using the median reading as the reported one.  In my testing so far I have a variance of about 1 to 4 mm which is plenty accurate for a consumer grade monitoring system.  It would appear that using the median reading all but eliminates the infrequent fringe type readings that could potentially give false positives.

Future versions will include;
- An offsite web component for viewing historical data, including graphs and water volume
- Proper push button shutdown to turn off the pi (raspi-atx)
- LCD panel to get a quick glance of the water lever without opening the lid.
- Proper mounting hardware and sturdy wire setup
- Material list and instructions for anyone else who would like to set up something similar for themselves

Further details provided at http://www.linuxnorth.org/raspi-sump/

