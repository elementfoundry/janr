# J.A.N.R. (just another network router)

![janr splash](/assets/images/JANR.png)
Welcome to J.A.N.R. (just another network router). A personal project to learn a bit more about networking and build out a router / ap. This project was designed around using an sbc as the core hardware of the project (an orange pi zero 2w). A gigabit usb to ethernet adapter was added, along with a second usb wifi adapter.

This project assumes that armbian is installed on the sbc. While it may work with other distrobutions no testing other than the orange pi mentioned earlier was used.

The result is a router / ap that handles two network endpoints, the orange pi's built in wifi for a 5ghz ap, and a usb wireless adapter for a 2.4ghz ap (my use case is using the 2.4g network for iot and legacy hardware)

The 5g ap currently tops out at about 150mbs network speed. This is due to the archicetural limits of using the built in wireless of this sbc. Another wireless usb adapter with better drivers and better hardware would probably allow network speeds of up to 300mbs on a 5g network.

Feel free to adapt or modify any of the code for your own use.