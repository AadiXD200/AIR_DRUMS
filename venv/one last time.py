from collections import deque
import simpleaudio as sa
import os

class DrumSound:
    def __init__ (self,name,):
        self.name = name
        self.sounds = []
        self.load()
    def load(self):
        for i in range(1, 6):
            path=r'C:\Users\aadi1\PycharmProjects\pythonProjecttriall chris\audio\\'+self.name+'\\'+self.name+str(i)+".wav"
            sound = sa.WaveObject.from_wave_file(path)
            self.sounds.append(sound)

    def play(self, volumeIndex):
        # Play loudest sound if given volume is greater than max
        if (volumeIndex > self.numberOfSounds - 1):
            self.sounds[self.numberOfSounds -1].play()
        # Play softest sound if less than 0
        elif (volumeIndex < 0):
            self.sounds[0].play()
        else:
            self.sounds[volumeIndex].play()

snare = DrumSound("Snare")
