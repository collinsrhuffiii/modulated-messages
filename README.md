# Transmit messages over FM

This project allows one to transmit message using an FM transmitter and a Software Defined Radio

## Demo

## Gear

[fm transmitter](https://www.amazon.com/Transmitter-Universal-Wireless-Modulator-Hands-Free/dp/B018QN4INM?ref_=Oct_RAsinC_Ajax_13981621_0&pf_rd_r=HYPJ70XTBZDEX86512J0&pf_rd_p=982c6428-962f-5497-bdb9-7d8edb4e2272&pf_rd_s=merchandised-search-6&pf_rd_t=101&pf_rd_i=13981621&pf_rd_m=ATVPDKIKX0DER)

[SDR](https://www.amazon.com/NooElec-NESDR-Mini-Compatible-Packages/dp/B009U7WZCA/ref=sr_1_3?keywords=realtek+sdr&qid=1573069453&sr=8-3)

## Dependencies

To transmit messages using the fm transmitter
[sounddevice](https://python-sounddevice.readthedocs.io/en/0.3.14/index.html)

To receive IQ samples from the SDR
[pyrtlsdr](https://github.com/roger-/pyrtlsdr)

pyrtlsdr depends on [rtl-sdr](https://osmocom.org/projects/rtl-sdr/wiki/Rtl-sdr)

For signal processing functions
[scipy](https://www.scipy.org/)

For real time graphing:
[PyQtGraph](http://www.pyqtgraph.org/)

## Encoding

To encode messages the messages, we first convert the string to bits. Next we, encapsulate the message in a very simple header, shown below.

### Message format

```
[ 1 1 1 1 1   0/1    0/1      0/1     0/1 0/1 0/1 ... ]
  ^ ^ ^ ^ ^    ^      ^        ^           ^
  preamble     id    frag   checksum     message
```


## Transmitting

To transmit our header and message, we use [Manchester encoding](https://en.wikipedia.org/wiki/Manchester_code) to represent each bit as a change from low to high or high to low. Then we create an AM signal from this encoding. Finally, we play the AM signal on the sound card, which sends it out of the FM transmitter. To make life easier for the receiver, we will only send messages on second boundaries. This will make it easier for the receiver to know if a transmission is taking place, as he/she only has to start capturing samples on second boundaries. Note, this makes syncing the clocks of the sender and receiver critical.

![Transmitted Signal](https://raw.githubusercontent.com/collinsrhuffiii/modulated-messages/master/assets/transmitted-signal.png)

## Receiving

To receive the signal, we first have to determine if a transmission is taking place. To do so, we first tune our SDR to the frequency agreed upon by the sender and receiver. As discussed in the Transmitting section, we will record samples starting at second boundaries. Next, we compute the Fast Fourier Transform of the captured samples. This decomposes the captured signal into its constituent frequencies. If the FFT at the agreed upon frequency is greater than some threshold, then we know a transmission is taking place. 

![FFT](https://raw.githubusercontent.com/collinsrhuffiii/modulated-messages/master/assets/fft.png)



## Decoding
Once we know a transmission is taking place. We must decode the signal to retrieve the message. To do so, we first FM demodulate the signal to get the AM signal. 

![FM Demodulated Signal](https://raw.githubusercontent.com/collinsrhuffiii/modulated-messages/master/assets/received-signal.png)

Next, we take the absolute value of the AM signal and find the envelope

![FM Demodulated Signal](https://raw.githubusercontent.com/collinsrhuffiii/modulated-messages/master/assets/envelope.png)

Next, we use thresholding to create a square wave. 

![FM Demodulated Signal](https://raw.githubusercontent.com/collinsrhuffiii/modulated-messages/master/assets/square-wave.png)

Finally, we decode the manchester encoded square wave to get the header and message as an array of bits. We then calculate a simple checksum (bit parity) and check the message id is the same as expected. If the fragment bit is set, we know that we should continue to wait for more transmissions. Otherwise, we print the message received.

## Graphing

PyQtGraph is used to graph the FFT and AM signal of the samples received. 
