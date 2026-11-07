# CarryDex

A PyQt desktop prototype that switches between a day-progress clock and push-to-talk speech notes with a radial transition.

## Run

Create and activate a Python virtual environment, then:

```bash
python -m pip install -r requirements.txt
python main.py
```

Press **F1** for the clock and **F2** for the recorder. PyAudio may require PortAudio or a compatible OS-specific wheel.

## What works

- Live time and percentage of the current day completed.
- Hold-to-record speech recognition and timestamped local note logs.
- Keyboard switching between the two tools.

Microphone behavior depends on local hardware and the Google recognition service. Speech is sent to that service; use non-sensitive test phrases.

## Next

Fix log newline formatting, add save feedback, and test clock calculations independently from audio. Offline recognition would make a useful later milestone.

Built by [SimpleCaci](https://github.com/SimpleCaci).
