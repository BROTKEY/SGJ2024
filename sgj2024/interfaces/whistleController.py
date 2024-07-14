from sgj2024.interfaces.baseController import BaseController
from threading import Thread
import numpy as np
import pyaudio


class WhistleController(BaseController):
    def __init__(self):
        self.volume = 0.0
        self.freq = 0.0
        self.running = True

        self.format = pyaudio.paFloat32
        self.channels = 1
        self.sampling_rate = 44100
        self.buffer_size = 1024

        # Calibration Data
        # Minimum index in FFT data (= lowest frequency), everything below this is counted as 0
        self.freq_min = 10
        # Maximum index in FFT data (= highest frequency), everything above this is counted as 1
        self.freq_max = 50
        # Volume thersholds
        self.vol_min = 0.3
        self.vol_max = 30

        self.thread = Thread(target=self)


    def __call__(self):
        audio = pyaudio.PyAudio()
        stream = audio.open(format=self.format, channels=self.channels,
                rate=self.sampling_rate, input=True,
                frames_per_buffer=self.buffer_size)
        dv = self.vol_max - self.vol_min
        di = self.freq_max - self.freq_min
        
        freq_hist = []
        vol_hist = []
        
        while self.running:
            data = np.frombuffer(stream.read(self.buffer_size), dtype=np.float32)
            fft_data = np.abs(np.fft.fft(data))
            imax = np.argmax(fft_data)
            vmax = fft_data[imax]
            v = (vmax - self.vol_min) / dv
            f = (imax - self.freq_min) / di
            vol_hist.append(np.clip(v, 0., 1.))
            freq_hist.append(np.clip(f, 0., 1.))
            # Smooth out by averaging over last 5 samples
            if len(vol_hist) > 5:
                vol_hist.pop(0)
            if len(freq_hist) > 5:
                freq_hist.pop(0)
            self.volume = np.average(vol_hist)
            self.freq = np.average(freq_hist)

    def start(self):
        self.thread.start()
            
    def stop(self):
        self.running = False
        self.thread.join()

    def pollAxis(self) -> tuple[float, float]:
        """return the value of the analog axis in order of strength, direction"""
        return self.volume, (self.freq * 2 - 1) * np.pi