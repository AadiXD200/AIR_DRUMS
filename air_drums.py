"""
Air Drums - Virtual Drum Kit using Computer Vision
Tracks green objects via webcam and plays drum sounds
"""

from collections import deque
import os
import sys
import json
import numpy as np
import simpleaudio as sa
from threading import Thread
import cv2
import imutils
import time


class Stick:
    """Represents a drum stick being tracked"""
    def __init__(self, name):
        self.points = deque(maxlen=4)
        self.minPoint = 500
        self.isGoingDown = False
        self.min = 500
        self.name = name

    def getName(self):
        return self.name

    def setMin(self, min_val):
        self.min = min_val

    def getMin(self):
        return self.min

    def getIsGoingDown(self):
        return self.isGoingDown

    def updateIsGoingDown(self, isGoingDown):
        self.isGoingDown = isGoingDown

    def getPoints(self):
        return self.points

    def addPoint(self, x, y):
        if len(self.points) > 0:
            self.points.appendleft((x, y))
        else:
            self.points.append((x, y))

    def getX(self):
        if len(self.points) > 0:
            return self.points[0][0]
        return 0

    def getY(self):
        if len(self.points) > 0:
            return self.points[0][1]
        return 0


class DrumSound:
    """Handles loading and playing drum sound samples"""
    def __init__(self, name, audio_base_path):
        self.name = name
        self.sounds = []
        self.audio_base_path = audio_base_path
        self.load()

    def load(self):
        """Load all 5 volume variations for this drum type"""
        # Handle different case variations
        possible_names = [self.name, self.name.lower(), self.name.capitalize()]
        
        for name_variant in possible_names:
            folder_path = os.path.join(self.audio_base_path, name_variant)
            if os.path.exists(folder_path):
                break
        else:
            print(f"WARNING: Audio folder not found for {self.name}. Tried: {possible_names}")
            return

        loaded_count = 0
        for i in range(1, 6):
            # Try different naming conventions
            possible_files = [
                f"{name_variant}{i}.wav",
                f"{self.name}{i}.wav",
                f"{self.name.lower()}{i}.wav",
                f"{self.name.capitalize()}{i}.wav",
            ]
            
            file_found = False
            for filename in possible_files:
                filepath = os.path.join(folder_path, filename)
                if os.path.exists(filepath):
                    try:
                        sound = sa.WaveObject.from_wave_file(filepath)
                        self.sounds.append(sound)
                        loaded_count += 1
                        file_found = True
                        break
                    except Exception as e:
                        print(f"ERROR loading {filepath}: {e}")
            
            if not file_found:
                print(f"WARNING: Could not find audio file for {self.name} volume {i}")
                # Create a dummy sound (silent) to maintain indices
                self.sounds.append(None)

        if loaded_count == 0:
            print(f"ERROR: No audio files loaded for {self.name}!")
        elif loaded_count < 5:
            print(f"WARNING: Only {loaded_count}/5 audio files loaded for {self.name}")

    def play(self, volumeIndex):
        """Play sound at specified volume level (0-4)"""
        if len(self.sounds) == 0:
            return
        
        # Clamp volume index
        if volumeIndex < 0:
            volumeIndex = 0
        elif volumeIndex >= len(self.sounds):
            volumeIndex = len(self.sounds) - 1
        
        if self.sounds[volumeIndex] is not None:
            try:
                self.sounds[volumeIndex].play()
            except Exception as e:
                print(f"ERROR playing {self.name}: {e}")


class WebcamVideoStream:
    """Threaded video stream for better performance"""
    def __init__(self, src=0, width=800, height=600, name="WebcamVideoStream"):
        self.stream = cv2.VideoCapture(src)
        
        if not self.stream.isOpened():
            raise RuntimeError(f"Could not open camera {src}")
        
        self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        (self.grabbed, self.frame) = self.stream.read()
        
        if not self.grabbed:
            raise RuntimeError("Could not read from camera")
        
        self.name = name
        self.stopped = False

    def start(self):
        t = Thread(target=self.update, name=self.name, args=())
        t.daemon = True
        t.start()
        return self

    def update(self):
        while True:
            if self.stopped:
                return
            (self.grabbed, self.frame) = self.stream.read()

    def read(self):
        return self.frame

    def stop(self):
        self.stopped = True
        if self.stream.isOpened():
            self.stream.release()


class LandingPage:
    """Welcome screen with instructions for users"""
    
    @staticmethod
    def show():
        """Display landing page with instructions"""
        # Create a black window
        landing = np.zeros((600, 800, 3), dtype=np.uint8)
        
        # Title
        cv2.putText(landing, "AIR DRUMS", (200, 80), 
                   cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)
        cv2.putText(landing, "Virtual Drum Kit", (220, 130), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # Instructions
        instructions = [
            "HOW TO USE:",
            "",
            "1. Get something GREEN to use as drum sticks",
            "   (green marker, green paper, green object)",
            "",
            "2. Hold the GREEN object in your hand(s)",
            "",
            "3. Move up and down to 'hit' the virtual drums",
            "",
            "4. The screen is divided into 6 sections:",
            "   TOP ROW: Kick | Snare | Tom",
            "   BOTTOM ROW: Floor | Hi-Hat | Ride",
            "",
            "5. Hit harder = Louder sound!",
            "",
            "6. Press ANY KEY to start playing...",
            "",
            "   (Press 'Q' during play to quit)"
        ]
        
        y_offset = 180
        for line in instructions:
            if line.startswith("HOW TO USE:"):
                color = (0, 255, 255)
                font_scale = 0.8
                thickness = 2
            elif line and not line.startswith("   "):
                color = (255, 255, 255)
                font_scale = 0.6
                thickness = 1
            else:
                color = (200, 200, 200)
                font_scale = 0.5
                thickness = 1
            
            cv2.putText(landing, line, (50, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thickness)
            y_offset += 30
        
        # Draw sample drum zones
        zones = [
            (0, 0, 266, 300, "KICK"),
            (266, 0, 533, 300, "SNARE"),
            (533, 0, 800, 300, "TOM"),
            (0, 300, 266, 600, "FLOOR"),
            (266, 300, 533, 600, "HI-HAT"),
            (533, 300, 800, 600, "RIDE")
        ]
        
        colors = [(0, 255, 0), (255, 0, 0), (0, 0, 255),
                  (255, 255, 0), (255, 0, 255), (0, 255, 255)]
        
        overlay = landing.copy()
        for i, (x1, y1, x2, y2, label) in enumerate(zones):
            cv2.rectangle(overlay, (x1, y1), (x2, y2), colors[i], 2)
            cv2.putText(overlay, label, (x1 + 10, y1 + 25),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, colors[i], 1)
        
        cv2.addWeighted(overlay, 0.3, landing, 0.7, 0, landing)
        
        cv2.imshow("Air Drums - Instructions", landing)
        cv2.waitKey(0)
        cv2.destroyWindow("Air Drums - Instructions")


def load_config(config_path="config.json"):
    """Load configuration from JSON file"""
    default_config = {
        "color_detection": {
            "lower_bound": [30, 86, 14],
            "upper_bound": [97, 244, 255]
        },
        "camera": {
            "width": 800,
            "height": 600,
            "camera_index": 0
        },
        "drum_layout": {
            "zones": [
                {"name": "kick", "x1": 0, "y1": 0, "x2": 266, "y2": 300},
                {"name": "snare", "x1": 266, "y1": 0, "x2": 533, "y2": 300},
                {"name": "tom", "x1": 533, "y1": 0, "x2": 800, "y2": 300},
                {"name": "floor", "x1": 0, "y1": 300, "x2": 266, "y2": 600},
                {"name": "hat", "x1": 266, "y1": 300, "x2": 533, "y2": 600},
                {"name": "ride", "x1": 533, "y1": 300, "x2": 800, "y2": 600}
            ]
        },
        "motion_detection": {
            "min_movement": 20,
            "min_radius": 4,
            "volume_sensitivity": 100
        },
        "audio": {
            "base_path": "audio"
        }
    }
    
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                # Merge with defaults
                for key in default_config:
                    if key not in config:
                        config[key] = default_config[key]
                return config
        except Exception as e:
            print(f"Error loading config: {e}. Using defaults.")
            return default_config
    else:
        print(f"Config file not found. Using defaults.")
        return default_config


def get_base_path():
    """Get the base path of the application"""
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        base_path = sys._MEIPASS
    else:
        # Running as script
        base_path = os.path.dirname(os.path.abspath(__file__))
    return base_path


def trackStick(stick, config, frame_height):
    """Track stick movement and trigger drum sounds"""
    stick.setMin(min(stick.getMin(), stick.getY()))
    
    if len(stick.getPoints()) == 4:
        yDirection = stick.getPoints()[3][1] - stick.getPoints()[0][1]
        min_movement = config["motion_detection"]["min_movement"]
        
        if stick.getIsGoingDown() and yDirection < -min_movement:
            volume = frame_height - stick.getMin()
            volume_sensitivity = config["motion_detection"]["volume_sensitivity"]
            volume = int(volume / volume_sensitivity) - 1
            playDrumByPosition(stick.getX(), stick.getY(), volume, config)
            stick.setMin(frame_height)
            stick.updateIsGoingDown(False)
        
        if abs(yDirection) > min_movement and yDirection >= 0:
            stick.updateIsGoingDown(True)


def playDrumByPosition(x, y, volume, config):
    """Determine which drum to play based on position"""
    zones = config["drum_layout"]["zones"]
    
    for zone in zones:
        if zone["x1"] <= x < zone["x2"] and zone["y1"] <= y < zone["y2"]:
            drum_name = zone["name"]
            if drum_name in drums:
                drums[drum_name].play(volume)
            break


def draw_drum_zones(frame, config):
    """Draw drum zone boundaries on frame"""
    zones = config["drum_layout"]["zones"]
    colors = {
        "kick": (0, 255, 0),
        "snare": (255, 0, 0),
        "tom": (0, 0, 255),
        "floor": (255, 255, 0),
        "hat": (255, 0, 255),
        "ride": (0, 255, 255)
    }
    
    overlay = frame.copy()
    for zone in zones:
        name = zone["name"]
        color = colors.get(name, (128, 128, 128))
        x1, y1 = zone["x1"], zone["y1"]
        x2, y2 = zone["x2"], zone["y2"]
        
        cv2.rectangle(overlay, (x1, y1), (x2, y2), color, 2)
        cv2.putText(overlay, name.upper(), (x1 + 5, y1 + 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
    
    cv2.addWeighted(overlay, 0.2, frame, 0.8, 0, frame)


# Global drum instances
drums = {}


def main():
    """Main application loop"""
    global drums
    
    # Show landing page
    try:
        LandingPage.show()
    except Exception as e:
        print(f"Could not show landing page: {e}")
        print("\n" + "="*60)
        print("AIR DRUMS - Virtual Drum Kit")
        print("="*60)
        print("\nINSTRUCTIONS:")
        print("1. Hold a GREEN object in each hand")
        print("2. Move your hands up and down to 'hit' the drums")
        print("3. Screen divided into 6 zones (2x3 grid)")
        print("   - Top: Kick, Snare, Tom")
        print("   - Bottom: Floor, Hi-Hat, Ride")
        print("4. Press any key to start...")
        print("\n" + "="*60 + "\n")
        input("Press Enter to continue...")
    
    # Load configuration
    config = load_config()
    
    # Get base path for audio files
    base_path = get_base_path()
    audio_path = os.path.join(base_path, config["audio"]["base_path"])
    
    if not os.path.exists(audio_path):
        print(f"ERROR: Audio directory not found at: {audio_path}")
        print("Please ensure the 'audio' folder exists in the project directory.")
        return
    
    # Initialize drum sounds
    print("Loading drum sounds...")
    drum_types = ["kick", "snare", "tom", "floor", "hat", "ride"]
    
    for drum_type in drum_types:
        try:
            drums[drum_type] = DrumSound(drum_type, audio_path)
            print(f"  ✓ Loaded {drum_type}")
        except Exception as e:
            print(f"  ✗ Failed to load {drum_type}: {e}")
    
    if len(drums) == 0:
        print("ERROR: No drum sounds loaded. Cannot continue.")
        return
    
    # Initialize sticks
    center = deque(maxlen=2)
    center.appendleft((0, 0))
    center.appendleft((0, 0))
    leftStick = Stick("left")
    rightStick = Stick("right")
    
    # Get color detection bounds
    color_lower = tuple(config["color_detection"]["lower_bound"])
    color_upper = tuple(config["color_detection"]["upper_bound"])
    
    # Get camera settings
    cam_width = config["camera"]["width"]
    cam_height = config["camera"]["height"]
    cam_index = config["camera"]["camera_index"]
    
    # Initialize video stream
    print("Initializing camera...")
    try:
        vs = WebcamVideoStream(src=cam_index, width=cam_width, height=cam_height).start()
        time.sleep(1.0)
    except Exception as e:
        print(f"ERROR: Could not initialize camera: {e}")
        print("Please check that your webcam is connected and not in use by another application.")
        return
    
    print("\n" + "="*60)
    print("Air Drums is running! Press 'Q' to quit.")
    print("="*60 + "\n")
    
    frameCount = 0
    
    try:
        while True:
            frame = vs.read()
            
            if frame is None:
                print("ERROR: Could not read frame from camera")
                break
            
            # Flip frame for mirror effect
            frame = cv2.flip(frame, 1)
            
            # Resize if needed
            if frame.shape[1] != cam_width or frame.shape[0] != cam_height:
                frame = cv2.resize(frame, (cam_width, cam_height))
            
            # Draw drum zones
            draw_drum_zones(frame, config)
            
            # Convert to HSV for color detection
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(hsv, color_lower, color_upper)
            mask = cv2.erode(mask, None, iterations=1)
            mask = cv2.dilate(mask, None, iterations=2)
            
            # Find contours
            cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cnts = imutils.grab_contours(cnts)
            cnts = sorted(cnts, key=lambda x: cv2.contourArea(x), reverse=True)
            
            min_radius = config["motion_detection"]["min_radius"]
            numSticks = min(len(cnts), 2)
            
            # Track sticks
            for i in range(numSticks):
                ((x, y), radius) = cv2.minEnclosingCircle(cnts[i])
                if radius > min_radius:
                    center.appendleft((int(x), int(y)))
            
            for i in range(numSticks):
                if numSticks > 1:
                    if center[i][0] <= center[(i + 1) % 2][0]:
                        cv2.circle(frame, center[i], int(radius), (156, 76, 76), 3)
                        leftStick.addPoint(center[i][0], center[i][1])
                        if frameCount > 4:
                            trackStick(leftStick, config, cam_height)
                    else:
                        cv2.circle(frame, center[i], int(radius), (76, 76, 156), 3)
                        rightStick.addPoint(center[i][0], center[i][1])
                        if frameCount > 4:
                            trackStick(rightStick, config, cam_height)
                else:
                    if center[i][0] >= cam_width // 2:
                        leftStick.addPoint(center[i][0], center[i][1])
                        if frameCount > 4:
                            trackStick(leftStick, config, cam_height)
                    else:
                        rightStick.addPoint(center[i][0], center[i][1])
                        if frameCount > 4:
                            trackStick(rightStick, config, cam_height)
            
            # Display frame
            cv2.imshow("Air Drums - Press 'Q' to quit", frame)
            
            key = cv2.waitKey(1) & 0xFF
            frameCount += 1
            
            if key == ord("q") or key == ord("Q"):
                break
    
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"\nERROR during execution: {e}")
        import traceback
        traceback.print_exc()
    finally:
        vs.stop()
        cv2.destroyAllWindows()
        print("\nAir Drums closed. Thanks for playing!")


if __name__ == "__main__":
    main()

