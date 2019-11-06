#!/usr/bin/env python3

import numpy as np
from scipy import signal
import config


def get_envelope(wave):
    analytical_signal = signal.hilbert(wave)
    envelope = np.abs(analytical_signal)
    return envelope


def binary_slicer(envelope):
    avg = np.average(envelope) + .02
    sliced = [1 if x > avg else 0 for x in envelope]
    return sliced


def manchester(square_wave, samp_per_bit, threshold=None):
    if threshold is None:
        threshold = samp_per_bit / 1.5

    transitions = []
    for i in range(len(square_wave)-1):
        if square_wave[i] == 1 and square_wave[i+1] == 0:
            transitions.append((i, 0))
        if square_wave[i] == 0 and square_wave[i+1] == 1:
            transitions.append((i, 1))

    if not transitions:
        return []
    valid_transitions = [transitions[0]]
    for t, b in transitions[1:]:
        if np.abs(valid_transitions[-1][0] + (2*samp_per_bit) - t) < threshold:
            valid_transitions.append((t, b))

    bits = [b for _, b in valid_transitions]
    return bits


def checksum(packet):
    if len(packet) < config.packet_header_len:
        return False

    pos = config.packet_checksum_pos
    print(sum(packet[:pos] + packet[pos+1:]) % 2)
    return (sum(packet[:pos] + packet[pos+1:]) % 2) == packet[pos]


def bits2ascii(b):
    return ''.join(chr(int(''.join(x), 2)) for x in zip(*[iter(b)]*8))


def demux(packet):
    if not(len(packet) >= config.packet_header_len):
        if config.debug:
            print('Packet too short')
        return False, None, None
    if not(checksum(packet)):
        if config.debug:
            print('Packet failed checksum')
        return False, None, None
    if not(packet[config.packet_id_pos] == config.cur_id):
        if config.debug:
            print('Packet had incorrect id')
            print('packet id', packet[config.packet_id_pos])
            print('cur id', config.cur_id)
        return False, None, None

    valid = True
    config.cur_id = (config.cur_id + 1) % 2
    fragmented = (packet[config.packet_fragment_pos] == 1)
    bitstring = ''.join(str(b) for b in packet[config.packet_header_len:])
    ascii_str = bits2ascii(bitstring)
    message = ''
    for c in ascii_str:
        message += str(chr(ord(c)))
    return valid, message, fragmented
