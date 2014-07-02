Quick Setup
===========

Disclaimer: You could easily damage your raspberry pi if you do not take proper care to understand
the need to insert a resistor between the echo pin on the sensor and the GPIO pin on the Raspberry Pi.
If you choose to do this you do it at your own risk.


In home directory
=================
Create raspi-sump and raspi-sump/csv directories

Copy raspisump.py to /home/pi/raspi-sump

Make raspisump.py executable by running    sudo chmod +x raspisump.py


Edit raspi-sump.py
==================

change critical_level to appropriate value in "cm's".  This will generate alerts when the water
level gets higher then the specified depth.

To start set the level to 1000cm and let the script run for a while.  This will help you determine an appropriate value to enter later.  I set mine 5cm above when the pump usually triggers.
My pump triggers at 30cm of water depth so I set the critical level to 35cm which is below my backup pump.

Edit SMTP server info
======================
1-add username and password (if authentication needed)

2-enter SMTP Server and port (Remove authentication and StartTLS if not needed).  Google mail requires this but many ISP's simply allow their customers to freely use their SMTP server on port 25 without authentication.  Better yet, if your ISP allows you, set the SMTP server to localhost:25.  My ISP blocks port 25 traffic so I just use Gmail instead of their unreliable SMTP server.

3-change Email_From and Email_To values.  You can enter your sms email here for sms alerts.  Check with your cellular provider on how to send email sms messages to your cell phone.  If you have a smartphone with a data plan then you can simply use the email address you configured on your phone.

Hardware
========

Setup hardware (Please make sure you understand GPIO information on your pi).

You must use two resistors to create a voltage divider from the Sensor to the Pi.  There are various combinations of resistors that you can use, a google search for Voltage Divider Calculator will allow you to calculate which combination you can use to bring the voltage down from the echo pin to 3.3V.  I used a 470 Ohm and 1K Ohm resistor to bring the voltage down on the GPIO pin to 3.4 which is within a tolerable 5% level. I could have also use a 1K and 2K resistor to give me 3.333V
Four wires connected as follows from the sensor to the pi (note, this will require some soldering).  A floppy disk power connector fits nicely on the sensor. 

1-VCC pin to 5V pin on Pi (pin 2)

2-Ground pin to Ground on Pi (pin 6) 

3-Trig pin to GPIO

4-Echo pin to GPIO (need 470R resistor and 1K resistor to create a voltage divider.) In short, the 470 Ohm and 1K Ohm resistor are connected to one another with the Echo wire soldered between both of them to the GPIO pin.  The other end of the 1K resistor is then soldered to the Ground wire.

see http://www.linuxnorth.org/raspi-sump/ for information on pins I used.

Google soldering resistors for good information on how to do this if you have never done it.

Starting Raspi-Sump
===================
To start raspi-sump manually issue the command    sudo /home/pi/raspi-sump/raspisump.py &

To start Raspi-Sump on bootup add the following line at the end of /etc/rc.local just before the line 'exit 0'

/home/pi/raspi-sump/raspisump.py &

Do not forget the ampersand '&' as this will run the script as a background process.

To stop Raspi-Sump:
sudo killall 09 raspisump.py

To monitor the log file in the csv folder while raspi-sump is running;
tail -f 'csvlogfilename'
