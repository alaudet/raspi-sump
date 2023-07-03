# Contributing Guidelines to Raspi-Sump

Contributions are welcome.

1. Please open an issue in the tracker to suggest a change or fix before issuing the pull request.

2. All pull requests should be off of the **devel** branch and not off the master.

3. All additions to version 1.x must work for the user without modifying the raspisump.conf file. You can add items to the conf but the code must provide a default value in config_values.py if the conf file value is missing. Version 2 will refactor the changes if/when it is released.

4. All code submitted must be your own or be allowable to re-distribute under the MIT License.

5. Raspi-Sump should not have a dependency on external services that require a login in order to use. Please use available Python3 libraries when adding new functionality.

6. Please reasonably follow PEP8 guidelines for your code. For example, if you create a function, give it a docstring so others know what you are doing. Add comments to make your code clearer to others reading it. If your code is incomprehensible it will not be included.

7. I can't promise that all new features will be accepted. However the MIT license allows/welcomes you to fork the code and release an altered version under any license that you like. Please see the requirements under the MIT license when doing so.

8. Make sure your changes work before issuing the pull request. Adding a unittest is highly encouraged. Make sure any current unittests pass.

9. If you want to contribute we have a Discord group with a #code-discussion forum. It is not mandatory to join but highly encouraged and makes collaboration much easier. Email alaudet@linuxnorth.org to request an invite link.
