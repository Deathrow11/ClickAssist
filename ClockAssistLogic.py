from pynput import mouse as pynput_mouse
import time
import threading
import random
import collections

# Shared state
click_times = collections.deque()
boost = 10
mouse_button = "left"
measured_cps = 0
tolerance = 10
state = False 
_running = False       
_lock = threading.Lock()
_cps_thread = None
_listener = None
_ignore_auto_until = 0.0


def on_click(x, y, button, pressed):
    global _ignore_auto_until
    
    now = time.time()
    
    # Ignore clicks during auto-boost window
    if now < _ignore_auto_until:
        return
    
    # Check if it's the right button
    button_name = "left" if button == pynput_mouse.Button.left else "right"
    if button_name != mouse_button:
        return
    
    # Only count button presses, not releases
    if pressed:
        with _lock:
            click_times.append(now)


def get_current_cps():
    now = time.time()
    with _lock:
        # Remove clicks older than 1 second
        while click_times and click_times[0] < now - 1.0:
            click_times.popleft()
        return len(click_times)


def cps_monitor():
    global _running, measured_cps
    last_print = time.time()
    
    while _running:
        time.sleep(0.1)
        
        current_cps = get_current_cps()
        measured_cps = current_cps  # ← Always update, regardless of state or tolerance
        
        # Print once per second
        now = time.time()
        if now - last_print >= 1.0:
            last_print = now
        
        # Only trigger boost if enabled AND threshold reached
        if state and current_cps >= tolerance:
            on_tol_reached(current_cps)


def on_tol_reached(measured_cps: int):
    global _ignore_auto_until
    if state:
        min_b = max(1, boost // 2)
        boostamt = random.randint(min_b, boost)
        
        print(f"🚀 BOOST TRIGGERED! {measured_cps} CPS detected, adding {boostamt} clicks")
        
        _ignore_auto_until = time.time() + (boostamt * 0.02) + 0.1
        
        mouse_controller = pynput_mouse.Controller()
        target_button = pynput_mouse.Button.left if mouse_button == "left" else pynput_mouse.Button.right
        
        for i in range(boostamt):
            mouse_controller.click(target_button)
            time.sleep(0.02)


def start():
    global _running, _cps_thread, _listener
    if _running:
        return
    _running = True
    
    # Start pynput listener
    if _listener is None:
        _listener = pynput_mouse.Listener(on_click=on_click)
        _listener.start()
    
    # Start CPS monitor thread
    if _cps_thread is None or not _cps_thread.is_alive():
        _cps_thread = threading.Thread(target=cps_monitor, daemon=True)
        _cps_thread.start()


def stop():
    global _running, _listener
    _running = False
    if _listener:
        _listener.stop()


def toggle(current_state):
    global state
    new_enabled = not current_state[1]
    state = new_enabled
    print(f"State toggled: {'ENABLED' if state else 'DISABLED'}")
    return ("Enabled", True) if new_enabled else ("Disabled", False)


def set_tolerance(value: int):
    global tolerance
    tolerance = max(1, int(value))
    print(f"Tolerance -> {tolerance}")


def set_boost(value: int):
    global boost
    boost = max(1, int(value))
    print(f"Boost -> {boost}")


def set_mouse_button(button: str):
    global mouse_button
    if button in ("left", "right"):
        mouse_button = button
        print(f"Mouse button -> {mouse_button}")


if __name__ == "__main__":
    start()
    state = True
    print("ClickAssist logic running (standalone). Press Ctrl+C to exit.")
    print("Click rapidly to test CPS detection...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        stop()