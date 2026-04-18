# Raspi-Sump and Security

## LAN based Appliance

Raspi-Sump is a LAN based appliance.  It should not be directly exposed to the wider Internet.

It is highly recommended to connect to your network from a VPN like Wireguard or OpenVPN, or with a service like Tailscale.

While every attempt is made to secure Raspi-Sump as much as possible there can still be vulnerabilities that allow an attacker with web access to Raspi-Sump to cause havoc with your instance.  For this reason direct Internet exposure is **NOT SUPPORTED**.


## Security Measures and Mitigations

As this is a LAN Based appliance Raspi-Sump does not enforce strong password authentication.  It allows you to access it on your private LAN easily.

That being said if you are bound and determined to connect Raspi-Sump to the wider Internet the following mitigations are recommended;

* Choose a strong password (minimum 16 characters with a mix of Upper and Lower Case, Numbers and Symbols)

* Implement a firewall on your Raspberry Pi with Netfilter or IPtables which only allows port 443 https access.  (if at home port forward to `ip of your pi port 443`)

* If you are connecting from a remote network that has a static IP then only allow that IP to connect to your Raspi-Sump web interface.

* consider segregating Raspi-Sump on its own secure VLAN so that it cannot interact with any other computers on your home network

* Sign your https TLS cert with Letsencrypt. The install created self signed cert is valid for 10 years.  This is acceptable on a LAN appliance.  Letsencrypt on validates certs for 3 months.  You should also consider a shorter rotation period for your self signed certs.  

* Consider forking Raspi-Sump for your specific internet use case and implement some kind of two factor authentication for your app.  This is way above the scope of Raspi-Sump and adds complexity I am not willing to implement on a LAN based appliance at this time, but you should consider if exposing to the wider internet.


**Ultimately there is no reason to not implement a VPN to your home or use a service like Tailscale which effectively creates a secure "Intranet like" environment for your remote devices and is built on top of Wireguard.**

## Security Implementations in Raspi-Sump

Raspi-Sump does provide the following;

* Cross site vulnerability hardening to mitigate malicious POST requests against session highjacking.

* Defense against brute force password attacks that tarpits multiple requests over a small time window.

* A dedicated `credentials.conf` file with tighter restrictions in `/etc/raspi-sump/`