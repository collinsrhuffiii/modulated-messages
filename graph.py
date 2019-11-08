#!/bin/env python3

import receive
import config

import scipy
import numpy as np
import time
import zmq

from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg

global fft_plot
global fft_curve
global am_plot
global am_curve
global zmq_socket


def configure_qt():
    app = QtGui.QApplication([])

    win = pg.GraphicsLayoutWidget(show=True, title="SDR Receiver")
    win.resize(1000, 600)
    win.setWindowTitle('Sdr')

    # Enable antialiasing for prettier plots
    pg.setConfigOptions(antialias=True)

    fft_plot = win.addPlot(title="FFT plot")
    fft_curve = fft_plot.plot(pen='y')

    win.nextRow()

    am_plot = win.addPlot(title="AM plot")
    am_curve = am_plot.plot(pen='b')

    return app, win, fft_plot, fft_curve, am_plot, am_curve


def configure_zmq_server():
    context = zmq.Context()
    #  Socket to talk to the sdr receiver
    print("Connecting to sdr receiver…")
    socket = context.socket(zmq.SUB)
    socket.setsockopt_string(zmq.SUBSCRIBE, '')
    socket.bind(config.zmq_path)
    return socket


def recv_array(socket, flags=0, copy=True, track=False):
    """recv a numpy array"""
    md = socket.recv_json(flags=flags)
    msg = socket.recv(flags=flags, copy=copy, track=track)
    buf = memoryview(msg)
    A = np.frombuffer(buf, dtype=md['dtype'])
    return A.reshape(md['shape'])


def update_fft(samples):
    fft = scipy.fftpack.fft(samples)
    freqs = scipy.fftpack.fftfreq(len(samples)) * config.rec_samp_rate
    fft_curve.setData(freqs, np.abs(fft))
    fft_plot.enableAutoRange('xy', False)


def update_am(samples):
    wave, new_samp_rate = receive.fm_demodulate(samples,
                                                config.frequency,
                                                config.offset,
                                                config.rec_samp_rate)
    am_curve.setData(wave)
    am_plot.enableAutoRange('y', False)


def update():
    try:
        samples = recv_array(zmq_socket, zmq.DONTWAIT)
    except zmq.error.Again:
        return

    n = len(samples)
    if n:
        update_fft(samples)
        update_am(samples)


if __name__ == '__main__':
    zmq_socket = configure_zmq_server()

    app, win, fft_plot, fft_curve, am_plot, am_curve = configure_qt()
    timer = QtCore.QTimer()
    timer.timeout.connect(update)

    # Start the timer on 1 second interval
    now = time.time()
    epsilon = .001
    while(now - int(now) > epsilon):
        now = time.time()
    print(f'time: {time.time()}')
    timer.start(1)

    # Start Qt event loop unless running in interactive mode or using pyside.
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
