#!/usr/bin/env python3

import sys
import sounddevice as sd
import numpy as np
import time
import config as config


def encode_manchester(bits):
    manchester = np.array([[False, True] if b else [True, False] for b in bits])
    manchester = np.reshape(manchester, (-1, 1))
    return manchester


def generate_am_signal(manchester_encoding, frequency,
                       samp_per_bit, num_samples, samp_rate):

    M = np.tile(manchester_encoding, (1, int(samp_per_bit)))
    t = np.r_[0.0:2*num_samples]/samp_rate
    am_signal = M.ravel()*np.sin(2*np.pi*frequency*t)
    return am_signal, t


def transmit(data):

    # Only allow transmissions to take up 1/2 of a second
    n = config.baud//2

    # Make sure n is a multiple of 8
    n -= n % 8
    data_frags = [data[i:i+n] for i in range(0, len(data), n)]
    num_frags = len(data_frags)
    checksum = '0'

    preamble = [1 for _ in range(config.len_preamble)]
    for i, data in enumerate(data_frags):
        packet_id = str(bin(config.cur_id))[2:]
        config.cur_id = (config.cur_id + 1) % 2
        if num_frags > 1 and i < num_frags - 1:
            fragmented = '1'
        else:
            fragmented = '0'

        packet = preamble + [int(packet_id), int(fragmented), int(checksum)] + [int(d) for d in data]
        parity = sum(packet) % 2
        packet[config.packet_checksum_pos] = parity
        print(packet)

        samp_per_bit = config.transmit_samp_rate/config.baud
        num_samples = len(packet) * samp_per_bit
        manchester = encode_manchester(packet)
        am_signal, t = generate_am_signal(manchester, config.frequency, samp_per_bit,
                                          num_samples, config.transmit_samp_rate)

        if config.save_samples:
            np.save(f'{config.path}/am_signal', np.array(am_signal))
            np.save(f'{config.path}/t', np.array(t))
        for _ in range(config.repeat_transmission):
            now = time.time()
            epsilon = .001
            while(now - int(now) > epsilon):
                now = time.time()
            sd.play(am_signal, blocking=True)


if __name__ == '__main__':
    while True:
        message = input("Enter the message to send:\n")
        message_bitstring = ''
        for c in message:

            # convert each character in the message to bits
            bits = str(bin(ord(c)))[2:]

            # pad the front of the message with 0's
            message_bitstring += ''.join('0' for _ in range(8-len(bits))) + bits

        transmit(message_bitstring)
