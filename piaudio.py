import pyaudio
import wave
import numpy
import psutil, os
import time
import scipy.signal as signal
from multiprocessing import Process, Value, Lock
import pygame


def audio_loop(file, p, ratio, end, chunk_size, stop_proc):
    time.sleep(0.5)
    proc = psutil.Process(os.getpid())
    proc.nice(-5)
    time.sleep(0.02)
    print ('audio file is ' + str(file))
    while True:
        #chunk = 2048/2
        wf = wave.open(file, 'rb')
        time.sleep(0.03)
        data = wf.readframes(chunk_size.value)
        time.sleep(0.03)

        stream = p.open(
            format = p.get_format_from_width(wf.getsampwidth()), 
            channels = wf.getnchannels(),
            rate = wf.getframerate(),
            output = True,
            frames_per_buffer = chunk_size.value)
        
        while data != '' and stop_proc.value == 0:
            #need to try locking here for multiprocessing
            array = numpy.fromstring(data, dtype=numpy.int16)
            result = numpy.reshape(array, (array.size/2, 2))
            #split data into seperate channels and resample
            final = numpy.ones((1024,2))
            reshapel = signal.resample(result[:, 0], 1024)

            final[:, 0] = reshapel
            reshaper = signal.resample(result[:, 1], 1024)
            final[:, 1] = reshaper
            out_data = final.flatten().astype(numpy.int16).tostring()
            #data = signal.resample(array, chunk_size.value*ratio.value)
            #stream.write(data.astype(int).tostring())
            stream.write(out_data)
            round_data = (int)(chunk_size.value*ratio.value)
            if round_data % 2 != 0:
                round_data += 1
            data = wf.readframes(round_data)
        stream.stop_stream()
        stream.close()
        wf.close()
        p.terminate()
        
        if end or stop_proc.value == 1:
            break
    stream.stop_stream()
    stream.close()
    wf.close()
    p.terminate()




# Start audio in seperate process to be non-blocking
class Audio:
    def __init__(self, file, end=False):
        self.p = pyaudio.PyAudio()
        self.stop_proc = Value('i', 0)
        self.chunk = 2048
        self.file = file
        self.ratio = Value('d' , 1.0)
        self.chunk_size = Value('i', int(2048/2))
        self.end = end
        #pygame.mixer.init(44100, -16, 2 , 2048)
        #hey
        pygame.mixer.init(47000, -16, 2 , 4096)

    def start_audio_loop(self):
        self.p = Process(target=audio_loop, args=(self.file, self.p, self.ratio, self.end, self.chunk_size, self.stop_proc))
        self.p.start()
        
    def stop_audio(self):
        self.stop_proc.value = 1
        #self.p.terminate()
        self.p.join()

    def change_ratio(self, ratio):
        self.ratio.value = ratio

    def change_chunk_size(self, increase):
        if increase:
            self.chunk_size.value = int(2048/4)
        else:
            self.chunk_size.value = int(2048/2)

    def start_effect(self):
        self.effect = pygame.mixer.Sound(self.file)
        self.effect.play()

    def stop_effect(self):
        self.effect.stop()

    def start_effect_music(self):
        pygame.mixer.music.load(self.file)
        pygame.mixer.music.play()

    def stop_effect_music(self):
        pygame.mixer.music.fadeout(1)
            
        
          
