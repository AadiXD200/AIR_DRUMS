import os
import simpleaudio as sa
if os.path.exists(r"C:\\Users\\aadi1\\PycharmProjects\\pythonProjecttriall chris\\audioSnare\\Snae\\nare1.wav"):
    print("yessss")
else:
    print("nahhh")
if os.path.exists(r"C:\Users\aadi1\PycharmProjects\pythonProjecttriall chris\audio\snare\Snare2.wav"):
    print("yessss")
else:
    print("nahhh")
sound = sa.WaveObject.from_wave_file(r"C:\Users\aadi1\PycharmProjects\pythonProjecttriall chris\audio\snare\Snare2.wav")
path = r"C:\Users\aadi1\PycharmProjects\pythonProjecttriall chris\audio"+self.name+'\\'+self.name +self.name+str(i)+".wav"
print(path)