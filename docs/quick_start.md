Quick Setup
===========

Disclaimer: You could easily damage your raspberry pi if you do not take proper care to understand
the need to insert a resistor between the echo pin on the sensor and the GPIO pin on the Raspberry Pi.
If you choose to do this you do it at your own risk.


In home directory
Create raspi-sump and raspi-sump/csv directories

Copy raspy-sump.py to /home/pi/raspi-sump

Make raspy-sump.py executable by running sudo chmod +x raspi-sump.py


Edit raspi-sump.py
==================

change critical_level to appropriate value in "cm's".  This will generate alerts when the water
level gets within this distance of the sensor.

To start set the level to 1cm and let the script run for a while.  This will tell  you an appropriate value to enter later.  I set mine 5cm below when the pump usually triggers.
My pump triggers at 42cm from the sensor so I set the critical level to 37cm.

Edit SMTP server info
======================
1-add username and password (if authentication needed)

2-enter SMTP Server and port (Remove authentication and StartTLS if not needed)

3-change Email_From and Email_To values.  You can enter your sms email here for sms alerts.

Hardware
========

Setup hardware (Please make sure you understand GPIO information on your pi).

You must use two resistors to create a voltage divider from the Sensor to the Pi.  There are various combinations of resistors that you can use, a google search for Voltage Divider Calculator will allow you to calculate which combination you can use to bring the voltage down from the echo pin to 3.3V.  I used a 470 Ohm and 1K Ohm resistor to bring the voltage down on the GPIO pin to 3.4 which is within a tolerable 5% level. 
Four wires connected as follows from the sensor to the pi (note, this will require some soldering).  A floppy disk power connector fits nicely on the sensor.

1-VCC pin to 5V pin on Pi (pin 2)

2-Ground pin to Ground on Pi (pin 6)  (Connect to 1K resistor and bridge to echo line)

3-Trig pin to GPIO

4-Echo pin to GPIO (need 470R resistor and 1K resistor to create a voltage divider.) I will try and put a diagram up here in the future.  In short, the 470 Ohm and 1K Ohm resistor are connected to one another with the Echo wire soldered between both of them to the GPIO pin.  The other end of the 1K resistor is then soldered to the Ground wire.

see http://www.linuxnorth.org/raspi-sump/ for information on pins I used.

Google soldering resistors for good information on how to do this if you have never done it.

Starting Raspi-Sump
===================
sudo /home/pi/raspi-sump/raspi-sump.py &

To start Raspi-Sump on bootup add the following line at the end of /etc/rc.local just before the line 'exit 0'

/home/pi/raspi-sump/raspi-sump.py &

Do not forget the ampersand '&' as this will run the script as a background process.

To stop Raspi-Sump:
sudo killall 09 raspi-sump.py

To monitor the log file in the csv folder while raspi-sump is running;
tail -f 'csvlogfilename'
