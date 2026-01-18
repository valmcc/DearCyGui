import dearcygui as dcg
import asyncio
import threading
from dearcygui.utils.asyncio_helpers import (
    AsyncThreadPoolExecutor,
    run_viewport_loop,
)
C = dcg.Context()

with dcg.Window(C, label="Test Window", width=800, height=600) as window:
    tab_bar = dcg.TabBar(C, reorderable=True)

    with dcg.Tab(C, label="Tab 1", parent=tab_bar) as tab1:
        dcg.Text(C, value="Content for Tab 1")
        dcg.Button(C, label="Button 1")
        plot1 = dcg.Plot(C, width=-1, height=-1)

    with dcg.Tab(C, label="Tab 2", parent=tab_bar) as tab2:
        dcg.Text(C, value="Content for Tab 2")
        dcg.Button(C, label="Button 2")
        plot2 = dcg.Plot(C, width=-1, height=-1)

    with dcg.Tab(C, label="Tab 3", parent=tab_bar) as tab3:
        dcg.Text(C, value="Content for Tab 3")
        dcg.Button(C, label="Button 3")
        plot3 = dcg.Plot(C, width=-1, height=-1)


def cycle_tabs(s, t, d):
    """Cycle through tabs when Tab is pressed."""
    print("Pressed Tab!")
    tabs = [c for c in tab_bar.children if isinstance(c, dcg.Tab)]
    if len(tabs) < 2:
        return

    # Find active tab
    active_idx = 0
    for i, tab in enumerate(tabs):
        if tab.value:
            active_idx = i
            break

    # Determine direction
    if C.is_key_down(dcg.Key.LEFTSHIFT) or C.is_key_down(dcg.Key.RIGHTSHIFT):
        next_idx = (active_idx - 1) % len(tabs)
    else:
        next_idx = (active_idx + 1) % len(tabs)

    print(f"Switching from {tabs[active_idx].label} to {tabs[next_idx].label}")

    # KEY INSIGHT: Set the value ONCE (not every frame!)
    # This triggers SetSelected flag for exactly ONE frame
    tabs[next_idx].value = True
    C.viewport.wake()

    # Schedule a verification check after a few frames
    def verify_and_retry():
        # Check if it actually switched
        actually_active = None
        for i, tab in enumerate(tabs):
            if tab.value:
                actually_active = i
                break

        if actually_active != next_idx:
            print(f"  Switch failed (still on {tabs[actually_active].label}), retrying...")
            # Retry ONCE more
            tabs[next_idx].value = True
            C.viewport.wake()

            # Check again after another delay
            def verify_final():
                actually_active2 = None
                for i, tab in enumerate(tabs):
                    if tab.value:
                        actually_active2 = i
                        break
                if actually_active2 == next_idx:
                    print(f"  ✓ Switch successful on retry")
                else:
                    print(f"  ✗ Switch failed even after retry")

            threading.Timer(0.05, verify_final).start()
        else:
            print(f"  ✓ Switch successful on first try")

    # Wait 50ms (about 3 frames at 60fps) before checking
    threading.Timer(0.05, verify_and_retry).start()


C.viewport.wait_for_input = False

C.viewport.handlers += [
    dcg.KeyPressHandler(C, key=dcg.Key.TAB, callback=cycle_tabs)
]

C.viewport.initialize()
loop = asyncio.new_event_loop()
while C.running:
    loop.run_until_complete(run_viewport_loop(C.viewport))
