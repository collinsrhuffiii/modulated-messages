#!/usr/bin/env python3

import numpy as np
from scipy import signal
import scipy.fftpack
from rtlsdr import RtlSdr
import asyncio
import time
import decode
import config


def configure_sdr(frequency, offset, sample_rate):
    sdr = RtlSdr()
    center_frequency = frequency - offset 
    sdr.sample_rate = sample_rate
    sdr.center_freq = center_frequency
    sdr.gain = 'auto'
    return sdr


def fm_demodulate(samples, frequency, offset, samp_rate):
    x1 = np.array(samples).astype("complex64")

    # To mix the data down, generate a digital complex exponential
    # (with the same length as x1) with phase -F_offset/Fs
    fc1 = np.exp(-1.0j * 2.0 * np.pi * offset/samp_rate*np.arange(len(x1)))

    # Now, just multiply x1 and the digital complex exponential
    x2 = x1 * fc1

    # An FM broadcast signal has  a bandwidth of 200 kHz
    f_bw = 200000
    n_taps = 64
    # Use Remez algorithm to design filter coefficients

    lpf = signal.remez(n_taps, [0, f_bw, f_bw+(samp_rate/2-f_bw)/4, samp_rate/2],
                       [1, 0], Hz=samp_rate)
    x3 = signal.lfilter(lpf, 1.0, x2)

    dec_rate = int(samp_rate / f_bw)
    x4 = x3[0::dec_rate]

    # Calculate the new sampling rate
    new_samp_rate = samp_rate/dec_rate

    # Polar discriminator
    y5 = x4[1:] * np.conj(x4[:-1])
    x5 = np.angle(y5)

    # The de-emphasis filter
    d = new_samp_rate * 75e-6   # Calculate the # of samples to hit the -3dB point
    x = np.exp(-1/d)            # Calculate the decay between each sample
    b = [1-x]                   # Create the filter coefficients
    a = [1, -x]
    x6 = signal.lfilter(b, a, x5)

    # Find a decimation rate to achieve audio sampling rate between 44-48 kHz
    audio_freq = 44100
    dec_audio = int(new_samp_rate/audio_freq)
    Fs_audio = new_samp_rate / dec_audio

    x7 = signal.decimate(x6, dec_audio)
    return x7, Fs_audio


def smooth(x, window_len=11, window='hanning'):
    s = np.r_[x[window_len-1:0:-1], x, x[-2:-window_len-1:-1]]
    if window == 'flat':
        w = np.ones(window_len, 'd')
    else:
        w = eval('numpy.' + window + '(window_len)')

    y = np.convolve(w/w.sum(), s, mode='valid')
    return y


def detect_transmitter_on(samples, samp_rate, offset,
                          offset_window=1, fft_window_size=100000,
                          freq_magnitude_threshold=10000):

    fft = scipy.fftpack.fft(samples)
    freqs = scipy.fftpack.fftfreq(len(samples)) * samp_rate
    index = np.where(np.abs(freqs - offset) < offset_window)[0]
    if index.size == 0:
        return False
    index = index[0]

    return (np.max(np.abs(fft)[index-fft_window_size:index+fft_window_size])
            > freq_magnitude_threshold)


def detect_transmission_present(wave, amplitude_threshold, count_threshold):
    return (np.abs(wave[:5000]) > amplitude_threshold).sum() > count_threshold


def detect_transmission_start(wave, window_size=100,
                              amplitude_threshold=.5, count_threshold=10):

    for i in range(len(wave)-window_size):
        if (np.abs(wave[i:i+window_size]) > amplitude_threshold).sum() > count_threshold:
            return i
    return 0


if __name__ == '__main__':
    samp_per_bit = config.rec_samp_rate/config.baud
    sdr = configure_sdr(config.frequency, config.offset, config.rec_samp_rate)

    async def streaming():
        fragmented = False
        message = ''
        async for samples in sdr.stream(num_samples_or_bytes=config.rec_samp_rate):
            if not(detect_transmitter_on(samples, config.rec_samp_rate, config.offset)):
                print('Transmitter off')
            else:
                wave, new_samp_rate = fm_demodulate(samples, config.frequency, config.offset, config.rec_samp_rate)
                samp_per_bit = new_samp_rate/config.baud
                detected = detect_transmission_present(wave, .5, 1)
                if detected:
                    start = detect_transmission_start(wave) - 500
                    end = len(wave) - detect_transmission_start(wave[::-1]) + 500

                    if start >= 0 and end <= len(wave):
                        smoothed_wave = smooth(np.abs(wave[start:end]), window_len=21, window='flat')
                        envelope = decode.get_envelope(smoothed_wave)[10:-10]
                        square_wave = decode.binary_slicer(envelope)
                        rec_bits = decode.manchester(square_wave, samp_per_bit)
                        if config.debug:
                            print(rec_bits)
                        valid, received_msg, fragmented = decode.demux(rec_bits)
                        if valid:
                            if config.save_samples:
                                np.save(f'samples/rec', samples)

                            message += received_msg
                            if message and not fragmented:
                                print('Received message:')
                                print(message)
                                print()
                                message = ''

    now = time.time()
    epsilon = .001
    while(now - int(now) > epsilon):
        now = time.time()
    print(f'time: {time.time()}')
    loop = asyncio.get_event_loop()
    loop.run_until_complete(streaming())
