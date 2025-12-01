# Air Drums 🥁

 **Live Application**: [https://air-drums-m7jm.vercel.app](https://air-drums-m7jm.vercel.app)

A virtual drum kit application that uses computer vision to track colored objects via webcam and plays drum sounds in real-time. **Now available as a web application!**

## Features

- **Web Application**: Live at [air-drums-m7jm.vercel.app](https://air-drums-m7jm.vercel.app) - No installation needed!
- **Custom Color Detection**: Choose any color to track (not just green!)
- **Real-time Computer Vision Tracking**: Tracks colored objects via webcam using JavaScript
- **6 Drum Types**: Kick, Snare, Tom, Floor Tom, Hi-Hat, and Ride cymbal
- **Volume Sensitivity**: Hit harder for louder sounds (5 volume levels per drum)
- **Multi-Stick Support**: Use up to 2 sticks simultaneously
- **Interactive Landing Page**: Professional, user-friendly interface
- **Configurable Settings**: Adjust colors, zones, and sensitivity via config file

## Requirements

- Python 3.7+
- Webcam
- Green objects to use as drum sticks (green markers, colored sticks, etc.)

## Installation

1. **Clone or download this repository**

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   - On macOS/Linux: `source venv/bin/activate`
   - On Windows: `venv\Scripts\activate`

4. **Install dependencies**:
   ```bash
   # For web application (Flask only)
   pip install -r requirements.txt
   
   # For desktop application (full dependencies)
   pip install -r requirements-full.txt
   ```

## Quick Start (Web Application)

1. **Visit the live site**: [https://air-drums-m7jm.vercel.app](https://air-drums-m7jm.vercel.app)

2. **Click "Start Playing"** on the landing page

3. **Allow camera access** when prompted

4. **Select a color** from the color picker (green, blue, red, yellow, purple, orange, or custom)

5. **Hold a colored object** in your hand(s) matching the selected color

6. **Move your hands up and down** to "hit" the virtual drums

7. **Hit different zones**:
   - **Top Row (Left to Right)**: Kick, Snare, Tom
   - **Bottom Row (Left to Right)**: Floor, Hi-Hat, Ride

8. **Enjoy making music!** 🎵

## Desktop Application Usage

For the desktop version (requires Python):

1. **Run the application**:
   ```bash
   python air_drums.py
   ```

2. **Read the instructions** on the landing page, then press any key to start

3. **Hold a colored object** in each hand

4. **Move your hands up and down** to "hit" the virtual drums

5. **Press 'Q'** to quit

## How It Works

The application divides your webcam view into 6 zones (2 rows × 3 columns). Each zone corresponds to a different drum sound:

```
┌─────────┬─────────┬─────────┐
│  KICK   │  SNARE  │   TOM   │
├─────────┼─────────┼─────────┤
│  FLOOR  │  HI-HAT │  RIDE   │
└─────────┴─────────┴─────────┘
```

When you move a green object downward in a zone, it detects the motion and plays the corresponding drum sound. The speed/depth of your strike determines the volume.

## Configuration

You can customize the application by editing `config.json`:

- **Color Detection**: Adjust HSV values to detect different colors
- **Camera Settings**: Change resolution and camera index
- **Drum Zones**: Modify zone positions and sizes
- **Motion Detection**: Adjust sensitivity and minimum movement thresholds

## Troubleshooting

### Camera not working
- Ensure no other application is using your webcam
- Try changing `camera_index` in `config.json` (try 0, 1, or 2)

### Colored objects not detected
- Ensure good lighting
- Use a bright, solid color (avoid transparent materials)
- Try selecting a different color from the color picker
- Check that the colored object is clearly visible in the camera view
- For web app: Use the color picker to match your object's color

### No sound playing
- Check that audio files exist in the `audio/` folder
- Ensure your system volume is turned up
- Check console for error messages about missing audio files

### Audio files not loading
- Verify folder names match: `kick/`, `snare/`, `tom/`, `floor/`, `hat/`, `ride/`
- Ensure each folder contains files named like: `Kick1.wav`, `Kick2.wav`, etc.

## Project Structure

```
AIR_DRUMS/
├── air_drums.py          # Main application
├── config.json           # Configuration file
├── requirements.txt      # Python dependencies
├── README.md            # This file
├── audio/               # Drum sound samples
│   ├── kick/
│   ├── snare/
│   ├── tom/
│   ├── floor/
│   ├── hat/
│   └── ride/
└── venv/                # Virtual environment (gitignored)
```

## Technical Details

### Web Application
- **Frontend**: HTML5, CSS3, JavaScript with Canvas API
- **Backend**: Flask (Python) for serving static files and API endpoints
- **Computer Vision**: Client-side JavaScript for color detection and tracking
- **Audio**: Web Audio API for low-latency sound playback
- **Deployment**: Vercel (serverless functions)
- **Live URL**: [air-drums-m7jm.vercel.app](https://air-drums-m7jm.vercel.app)

### Desktop Application
- **Computer Vision**: OpenCV for color detection and contour tracking
- **Audio**: SimpleAudio for low-latency WAV file playback
- **Motion Detection**: Tracks position history to detect downward strikes
- **Multi-threading**: Separate thread for video capture to improve performance

## Credits

Created as a fun computer vision project. Uses OpenCV, SimpleAudio, and various other open-source libraries.

## License

Feel free to use and modify this project for your own purposes!

## Tips for Best Experience

1. **Use bright, solid green objects** - Avoid transparent or reflective materials
2. **Good lighting** - Natural or bright artificial light works best
3. **Solid background** - Avoid green backgrounds or clothing
4. **Distance** - Stay 2-4 feet from the camera for best tracking
5. **Practice** - It takes a moment to get used to the virtual drum zones

Enjoy making music! 


