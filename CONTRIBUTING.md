Contributing Guidelines to Raspi-Sump
==================

Contributions are welcome.

1) Please open an issue in the tracker to suggest a change or fix before issuing the pull request.  

2) All pull requests should be off of the __devel__ branch and not off the master.

3) All additions to version 1.x must work for the user without modifying the raspisump.conf file.  You can add items to the conf but the code must provide a default value if the conf file value is missing.  Version 2 will refactor the changes if/when it is released.

4) All code submitted must be your own or be allowable to distribute under the MIT license.

5) I can't promise that all new features will be accepted.  However the MIT license allows/welcomes you to fork the code and release an altered version under any license that you like.  Please see the requirements under the MIT license when doing so.

6) Make sure your changes work before issuing the pull request.  Adding a nosetest is welcome.  Make sure any current nosetests pass.

