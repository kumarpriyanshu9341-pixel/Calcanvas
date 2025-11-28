
import cv2
import mediapipe as mp
import numpy as np
import math
import time
import threading
import speech_recognition as sr
import pyttsx3
from sympy import sympify, SympifyError
import pytesseract

# Mediapipe setup
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Initialize Mediapipe Hands
hands = mp_hands.Hands(min_detection_confidence=0.8, min_tracking_confidence=0.8)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

recognizer = sr.Recognizer()
engine = pyttsx3.init()


voice_active = False  # Global flag to control listening


# Configurable canvas size
canvas_height, canvas_width = 600, 640
canvas = np.ones((canvas_height, canvas_width, 3), dtype="uint8") * 255
drawing_mode = True  # Toggle between drawing and calculator modes
expression = ""

# Pencil and eraser settings
current_color = (0, 0, 0)  # Default color is black
brush_size = 3
is_eraser = False

# Color buttons
color_buttons = {
    'Red': (255, 0, 0),
    'Green': (0, 255, 0),
    'Blue': (0, 0, 255),
    'Yellow': (0, 255, 255)
}
button_height, button_width = 50, 50
color_button_start_x = canvas_width - button_width - 10  # Top-right corner
color_button_start_y = 10

# Virtual keyboard layout
keyboard_layout = [
    ['7', '8', '9', '/'],
    ['4', '5', '6', '*'],
    ['1', '2', '3', '-'],
    ['C', '0', '=', '+']
]
key_height, key_width = 100, 100
selection_hold_time = 1.0  # Time in seconds to confirm a selection
gesture_start_time = None
last_selected_key = None
last_position = None  # Track the last drawing position

# Distance threshold for pinch detection
pinch_threshold = 30  # Adjust based on the distance in pixels

# Draw virtual keyboard
def draw_virtual_keyboard(frame):
    global keyboard_layout
    for i, row in enumerate(keyboard_layout):
        for j, key in enumerate(row):
            x1, y1 = j * key_width, i * key_height
            x2, y2 = x1 + key_width, y1 + key_height
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, key, (x1 + 30, y1 + 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            
def detect_and_evaluate_math(canvas):
    import cv2

    # Convert the canvas to grayscale
    gray = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)

    # OCR to detect text
    expression = pytesseract.image_to_string(thresh, config='--psm 6').strip()
    expression = expression.replace('=', '').replace(' ', '')

    # Evaluate the math expression
    try:
        result = sympify(expression)
        print(f"Detected Expression: {expression} = {result}")
        return f"{expression} = {result}"
    except Exception as e:
        print(f"Error in expression: {expression}")
        return "Invalid Expression"

def recognize_text_from_canvas(canvas_image):
    speak("text mode is activated")
    gray = cv2.cvtColor(canvas_image, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(gray)
    print("Recognized Text:", text)

    with open("recognized_text.txt", "w", encoding='utf-8') as f:
        f.write(text)

    speak("Text has been recognized and saved to notepad.")


            
def speak(text):
    engine.say(text)
    engine.runAndWait()

def listen_for_shapes():
    global voice_active
    recognizer.energy_threshold = 4000
    while voice_active:
        with sr.Microphone() as source:
            print("Listening for shape commands...")
            audio = recognizer.listen(source, phrase_time_limit=4)
        try:
            command = recognizer.recognize_google(audio).lower()
            print("Command heard:", command)
            
            if "stop" in command or "exit" in command or "bye" in command:
                voice_active = False
                speak("Voice command stopped.")
                break
            elif "draw" in command:
                shape = command.replace("draw", "").strip()
                draw_shape(shape)
            elif "draw" in command:
                shape = command.replace("draw", "").strip()
                draw_shape(shape)
        except Exception as e:
            print("Voice recognition error:", e)

def draw_shape(shape):
    shape = shape.lower()
    center = (int(canvas_width / 2), int(canvas_height / 2))
    if shape == "circle":
        cv2.circle(canvas, center, 100, current_color, -1)
        speak("Drawing circle")
    elif shape == "rectangle":
        cv2.rectangle(canvas, (center[0]-100, center[1]-50), (center[0]+100, center[1]+50), current_color, -1)
        speak("Drawing rectangle")
    elif shape == "square":
        cv2.rectangle(canvas, (center[0]-100, center[1]-100), (center[0]+100, center[1]+100), current_color, -1)
        speak("Drawing square")
    elif shape == "star":
        draw_star(center)
        speak("Drawing star")
    elif shape == "pentagon":
        draw_polygon(center, 5)
        speak("Drawing pentagon")
    else:
        speak("I don't recognize that shape.")

def draw_polygon(center, sides, radius=100):
    angle = 2 * np.pi / sides
    points = [
        (int(center[0] + radius * np.cos(i * angle)),
         int(center[1] + radius * np.sin(i * angle)))
        for i in range(sides)
    ]
    cv2.polylines(canvas, [np.array(points)], isClosed=True, color=current_color, thickness=3)
    cv2.fillPoly(canvas, [np.array(points)], current_color)

def draw_star(center, radius=100):
    points = []
    for i in range(10):
        angle = i * np.pi / 5
        r = radius if i % 2 == 0 else radius / 2
        x = int(center[0] + r * np.cos(angle))
        y = int(center[1] + r * np.sin(angle))
        points.append((x, y))
    cv2.fillPoly(canvas, [np.array(points)], current_color)


# Draw color buttons, size buttons, and eraser button
def draw_color_size_eraser_buttons(frame):
    y = color_button_start_y
    for name, color in color_buttons.items():
        x1, y1 = color_button_start_x, y
        x2, y2 = x1 + button_width, y1 + button_height
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, -1)
        cv2.putText(frame, name[0], (x1 + 15, y1 + 35), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        y += button_height + 10

    # Brush size buttons
    cv2.rectangle(frame, (color_button_start_x, y), (color_button_start_x + button_width, y + button_height), (200, 200, 200), -1)
    cv2.putText(frame, "+", (color_button_start_x + 15, y + 35), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    y += button_height + 10
    cv2.rectangle(frame, (color_button_start_x, y), (color_button_start_x + button_width, y + button_height), (200, 200, 200), -1)
    cv2.putText(frame, "-", (color_button_start_x + 15, y + 35), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

    # Eraser button
    y += button_height + 10
    cv2.rectangle(frame, (color_button_start_x, y), (color_button_start_x + button_width, y + button_height), (100, 100, 100), -1)
    cv2.putText(frame, "E", (color_button_start_x + 15, y + 35), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

# Detect fingertip position
def get_fingertip_coords(landmarks):
    index_x = int(landmarks.landmark[8].x * canvas_width)
    index_y = int(landmarks.landmark[8].y * canvas_height)
    thumb_x = int(landmarks.landmark[4].x * canvas_width)
    thumb_y = int(landmarks.landmark[4].y * canvas_height)
    return (index_x, index_y), (thumb_x, thumb_y)

# Check if pinch gesture is made
def is_pinch(index_tip, thumb_tip):
    distance = math.hypot(index_tip[0] - thumb_tip[0], index_tip[1] - thumb_tip[1])
    return distance < pinch_threshold

# Check which key or button is hovered over
def check_hover(x, y):
    global keyboard_layout

    # Check for color, size, and eraser buttons
    y_btn = color_button_start_y
    for name in color_buttons:
        x1, y1 = color_button_start_x, y_btn
        x2, y2 = x1 + button_width, y1 + button_height
        if x1 <= x <= x2 and y1 <= y <= y2:
            return name
        y_btn += button_height + 10

    if color_button_start_x <= x <= color_button_start_x + button_width:
        if y_btn <= y <= y_btn + button_height:
            return "Increase"
        y_btn += button_height + 10
        if y_btn <= y <= y_btn + button_height:
            return "Decrease"
        y_btn += button_height + 10
        if y_btn <= y <= y_btn + button_height:
            return "Eraser"

    # Check for virtual keyboard
    row = y // key_height
    col = x // key_width
    if 0 <= row < len(keyboard_layout) and 0 <= col < len(keyboard_layout[0]):
        return keyboard_layout[row][col]
    return None

# Clear expression area on the canvas
def clear_expression_area():
    global canvas
    cv2.rectangle(canvas, (10, 10), (canvas_width - 10, 60), (255, 255, 255), -1)

# Evaluate mathematical expression
def evaluate_expression():
    global expression
    try:
        result = sympify(expression)
        return str(result)
    except (SympifyError, TypeError):
        return "Error"

# Main video capture and processing loop
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_frame)

    if drawing_mode:
        cv2.putText(frame, "Mode: Drawing", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        draw_color_size_eraser_buttons(frame)

        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                # Get fingertip coordinates
                index_tip, thumb_tip = get_fingertip_coords(hand_landmarks)

                # Check for pinch gesture
                if is_pinch(index_tip, thumb_tip):
                    hovered_button = check_hover(index_tip[0], index_tip[1])
                    if hovered_button in color_buttons:
                        current_color = color_buttons[hovered_button]
                        is_eraser = False
                    elif hovered_button == "Increase":
                        brush_size = min(20, brush_size + 1)
                    elif hovered_button == "Decrease":
                        brush_size = max(1, brush_size - 1)
                    elif hovered_button == "Eraser":
                        is_eraser = True

                    # Draw on canvas and overlay strokes on video feed
                    if last_position is not None:
                        if is_eraser:
                            cv2.line(canvas, last_position, index_tip, (255, 255, 255), brush_size)
                            cv2.line(frame, last_position, index_tip, (255, 255, 255), brush_size)
                        else:
                            cv2.line(canvas, last_position, index_tip, current_color, brush_size)
                            cv2.line(frame, last_position, index_tip, current_color, brush_size)
                    last_position = index_tip
                else:
                    last_position = None
    else:
        cv2.putText(frame, "Mode: Calculator", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        draw_virtual_keyboard(frame)

        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                index_tip, thumb_tip = get_fingertip_coords(hand_landmarks)
                if is_pinch(index_tip, thumb_tip):
                    hovered_key = check_hover(index_tip[0], index_tip[1])
                    if hovered_key:
                        if gesture_start_time is None or hovered_key != last_selected_key:
                            gesture_start_time = time.time()
                            last_selected_key = hovered_key
                        elif time.time() - gesture_start_time > selection_hold_time:
                            if hovered_key == "=":
                                clear_expression_area()
                                expression = evaluate_expression()
                            elif hovered_key == "C":
                                expression = ""
                                clear_expression_area()
                            else:
                                expression += hovered_key
                            last_selected_key = None
                            gesture_start_time = None

        clear_expression_area()
        cv2.putText(canvas, f"Expression: {expression}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    cv2.imshow("Webcam Feed", frame)
    cv2.imshow("Drawing Canvas", canvas)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('m'):
        drawing_mode = not drawing_mode
        if drawing_mode:
            canvas.fill(255)
            expression = ""
    elif key == ord('c'):
        speak("resetting")
        canvas.fill(255)
        expression = ""
    elif key == ord('v'):
        if not voice_active:
            voice_active = True
            threading.Thread(target=listen_for_shapes, daemon=True).start()
            speak("Listening for shape drawing commands.")
    elif key == ord('t'):
        recognize_text_from_canvas(canvas)
    elif key == ord('e'):
        result_text = detect_and_evaluate_math(canvas)
        cv2.putText(canvas, result_text, (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)

    elif key == 27:
        break

cap.release()
cv2.destroyAllWindows()
