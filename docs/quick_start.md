Quick Setup
===========

Disclaimer: You could easily damage your raspberry pi if you do not take proper care to understand
the need to insert a resistor between the echo pin on the sensor and the GPIO pin on the Raspberry Pi.
If you choose to do this you do it at your own risk.


In home directory
=================
Create raspi-sump and raspi-sump/csv directories

Copy raspisump.py to /home/pi/raspi-sump

Copy .raspisump.conf to /home/pi/raspi-sump

Make raspisump.py executable by running    sudo chmod +x raspisump.py

Copy checkpid.py to home/pi/raspi-sump

Make checkpid.py executable by running    sudo chmod +x checkpid.py

Edit .raspisump.conf 
====================

Do not edit the raspisump.py file.  All configurations for are recorded in .raspisump.conf


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

To check for the health of the raspisump.py process run the checkpid.py script as root
Add to root user crontab as follows;
1 - login as root
2 - crontab -e
3 - enter line in crontab as follows;
    5 * * * * /home/pi/raspisump/checkpid.py

This will check the raspisump.py process once per hour and restart the process if it is stopped.
