# Air Drums - Web Application

A professional web-based virtual drum kit application that uses computer vision to track green objects via webcam.

## Features

- 🌐 **Web-based** - Runs entirely in your browser
- 🎥 **Webcam Integration** - Uses your device's camera
- 🥁 **6 Drum Types** - Kick, Snare, Tom, Floor, Hi-Hat, and Ride
- 🔊 **Volume Control** - Hit harder for louder sounds
- 📱 **Responsive Design** - Works on desktop and mobile
- 🎨 **Professional UI** - Beautiful, modern interface

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Web Server

```bash
python app.py
```

### 3. Open in Browser

Navigate to: **http://localhost:5000**

You'll see a beautiful landing page with instructions!

## How to Use

1. **Click "Start Playing"** on the landing page
2. **Allow camera access** when prompted
3. **Click "Start Camera"** button
4. **Hold a GREEN object** in your hand(s)
5. **Move up and down** to hit the virtual drums
6. **Enjoy making music!** 🎵

## Project Structure

```
AIR_DRUMS/
├── app.py                 # Flask web server
├── templates/
│   ├── landing.html      # Landing page
│   └── play.html         # Drum interface
├── static/
│   ├── css/
│   │   ├── landing.css   # Landing page styles
│   │   └── play.css      # Play page styles
│   └── js/
│       └── play.js       # Main application logic
├── audio/                # Drum sound files
└── requirements.txt      # Python dependencies
```

## Web vs Desktop Version

This web version provides:
- ✅ Professional landing page
- ✅ Better user experience
- ✅ Cross-platform compatibility
- ✅ No installation needed (just run the server)
- ✅ Modern, responsive design

The desktop version (`air_drums.py`) is still available if you prefer it!

## Browser Compatibility

- ✅ Chrome/Edge (recommended)
- ✅ Firefox
- ✅ Safari
- ⚠️ Requires WebRTC support for camera access

## Troubleshooting

### Camera Not Working
- Ensure you've granted camera permissions
- Try a different browser
- Check that no other app is using the camera

### No Sound
- Check system volume
- Ensure audio files are in the `audio/` folders
- Check browser console for errors

### Green Object Not Detected
- Use a bright, solid green color
- Ensure good lighting
- Try adjusting the green threshold in `play.js`

## Customization

Edit `config.json` or modify the JavaScript in `play.js` to customize:
- Color detection sensitivity
- Drum zone positions
- Volume sensitivity
- Visual appearance

## Enjoy! 🥁🎵

