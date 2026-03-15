# Contributing Guidelines to Raspi-Sump

Contributions are welcome.

1. Please open an issue in the tracker to suggest a change or fix before issuing the pull request.

2. All pull requests should target the **devel** branch and not master/main.

3. All code submitted must be your own or be allowable to redistribute under the Apache 2.0 License.

4. Raspi-Sump should not depend on external services that require a login. Use available Python 3 libraries when adding new functionality. The one exception is Mastodon alerts — Mastodon is based on open source software and allows users to host their own instance. External services such as Twilio or Twitter are not allowed because they are subject to short-notice EULA or API changes that are not suitable for a freely available open source project.

5. All JavaScript and CSS libraries used in the web interface must be bundled in `raspisump/static/`. No CDN links are permitted. Raspi-Sump runs as a LAN appliance and must function without internet access.

6. New Python dependencies must be added to `debian/control` as well as the code. Contributions must not break the `.deb` build (`dpkg-buildpackage -us -uc -b`).

7. Follow PEP 8 guidelines for code style. Follow PEP 257 for docstrings — add a docstring to every function so others understand its purpose. Add comments where the intent is not immediately obvious. Code that is difficult to read will not be accepted.

8. New functionality must include a unittest. All existing tests must pass before issuing a pull request. Run the test suite with `pytest tests/` and confirm a clean result.

9. You may use AI assistants (such as Claude) to help write code. Be honest about your usage. Do not submit code you do not understand or that has no clear purpose. If the intent is unclear or it does not benefit the application, it will not be accepted.

10. I can't promise that all new features will be accepted. However, the Apache 2.0 license allows and welcomes you to fork the code and release an altered version under any compatible license. Please review the requirements of the Apache 2.0 license when doing so.

11. If you want to contribute, join the Discord group — there is a `#code-discussion` channel. It is not mandatory but makes collaboration much easier. Email [alaudet@linuxnorth.org](mailto:alaudet@linuxnorth.org) to request an invite link.
