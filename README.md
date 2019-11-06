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

## Encoding

### Message format

```
[ 1 1 1 1 1   0/1    0/1      0/1     0/1 0/1 0/1 ... ]
  ^ ^ ^ ^ ^    ^      ^        ^           ^
  preamble     id    frag   checksum     message
```


## Transmitting

## Receiving

## Decoding

## Graphing
