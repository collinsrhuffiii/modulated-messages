#!/usr/bin/env python3

path = '/home/ch/Downloads/radio/samples'
save_samples = False
debug = True

# Transmission/Reception Parameters
transmit_samp_rate = 44100
rec_samp_rate = 2**21
baud = 100
frequency = int(88.1e6)
offset = 150000
repeat_transmission = 1

# Packet parameters
len_preamble = 5
cur_id = 0
packet_id_pos = len_preamble
packet_fragment_pos = len_preamble + 1
packet_checksum_pos = len_preamble + 2
packet_header_len = len_preamble + 3
