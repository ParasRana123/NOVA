import keyboard

def mute():
    keyboard.press_and_release('volume mute')
def unmute():
    keyboard.press_and_release('volume up')
def next_track():
    """Skip to the next track."""
    keyboard.press_and_release("next track")

def previous_track():
    """Go to the previous track."""
    keyboard.press_and_release("previous track")

def type_message(message):
    """Automatically type a message."""
    keyboard.write(message)

def find_text():
    """Open the 'Find' dialog in most applications."""
    keyboard.press_and_release("ctrl+f")

def volume_up(steps=10):
    """Increase the volume."""
    for _ in range(steps):
        keyboard.press_and_release("volume up")

def volume_down(steps=10):
    """Decrease the volume."""
    for _ in range(steps):
        keyboard.press_and_release("volume down")
def play():
    keyboard.press_and_release("play/pause")
def handle_keyboard_action(command):
    """Respond to the selected action from the keyboard list."""
    if command == "increase":
        volume_up()
    elif command=="decrease":
        volume_down()
    elif command == "mute":
        mute()
    elif command=="unmute":
        unmute()
    elif command == "play" or command == "pause":
        play()
    elif command == "next track":
        next_track()
    elif command == "previous track":
        previous_track()
    elif command == "type":
        type_message("jarvis")
    elif command == "find":
        find_text()
    elif command == "screenshot":
        keyboard.press_and_release("print screen")
    elif command == "close":
        keyboard.press_and_release("alt+f4")
    else:
        print(f"Unknown command: {command}")

# Main logic to loop through the keyboardlist

# command = "play" 

