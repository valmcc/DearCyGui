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


# Track the switch - use a counter that increments every frame
switch_state = {"counter": 0, "target_idx": None}


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

    print(f"Initiating switch from {tabs[active_idx].label} (idx={active_idx}) to {tabs[next_idx].label} (idx={next_idx})")

    # Start the forced switch - use a high counter number
    switch_state["target_idx"] = next_idx
    switch_state["counter"] = 100  # Force for 100 frames (about 1.5 seconds at 60fps)

    # Immediately set the value
    tabs[next_idx].value = True
    C.viewport.wake()


def on_frame_render(s, t, d):
    """Called every frame - BEFORE tabs are drawn."""
    if switch_state["counter"] > 0:
        tabs = [c for c in tab_bar.children if isinstance(c, dcg.Tab)]
        target_idx = switch_state["target_idx"]

        # Force the target tab to True
        tabs[target_idx].value = True

        switch_state["counter"] -= 1

        if switch_state["counter"] == 0:
            # Verify it actually switched
            actually_active = None
            for i, tab in enumerate(tabs):
                if tab.value:
                    actually_active = i
                    break
            print(f"Switch attempt ended. Target was {tabs[target_idx].label}, actually active: {tabs[actually_active].label if actually_active is not None else 'NONE'}")

        C.viewport.wake()


C.viewport.wait_for_input = False

# Use a VIEWPORT handler so it runs early in the frame
C.viewport.handlers += [
    dcg.KeyPressHandler(C, key=dcg.Key.TAB, callback=cycle_tabs),
    dcg.RenderHandler(C, callback=on_frame_render)
]

C.viewport.initialize()
loop = asyncio.new_event_loop()
while C.running:
    loop.run_until_complete(run_viewport_loop(C.viewport))
