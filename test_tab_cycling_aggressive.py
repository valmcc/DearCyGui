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
        # Add a plot to simulate the issue
        plot1 = dcg.Plot(C, width=-1, height=-1)

    with dcg.Tab(C, label="Tab 2", parent=tab_bar) as tab2:
        dcg.Text(C, value="Content for Tab 2")
        dcg.Button(C, label="Button 2")
        plot2 = dcg.Plot(C, width=-1, height=-1)

    with dcg.Tab(C, label="Tab 3", parent=tab_bar) as tab3:
        dcg.Text(C, value="Content for Tab 3")
        dcg.Button(C, label="Button 3")
        plot3 = dcg.Plot(C, width=-1, height=-1)


# Track the switch state
switch_state = {"active": False, "counter": 0, "target_idx": None, "old_idx": None}


def cycle_tabs(s, t, d):
    """Cycle through tabs when Tab is pressed."""
    # Ignore if a switch is already in progress
    if switch_state["active"]:
        print("Switch already in progress, ignoring")
        return

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

    print(f"Initiating switch from {tabs[active_idx].label} to {tabs[next_idx].label}")

    # Start the switch process
    switch_state["active"] = True
    switch_state["counter"] = 0
    switch_state["target_idx"] = next_idx
    switch_state["old_idx"] = active_idx

    # Disable tab bar to prevent mouse interference
    tab_bar.enabled = False
    C.viewport.wake()


def on_frame_render(s, t, d):
    """Called every frame to manage the tab switch."""
    if not switch_state["active"]:
        return

    tabs = [c for c in tab_bar.children if isinstance(c, dcg.Tab)]
    target_idx = switch_state["target_idx"]
    old_idx = switch_state["old_idx"]

    # Force the switch every frame
    # First set old to False, then new to True
    tabs[old_idx].value = False
    tabs[target_idx].value = True

    switch_state["counter"] += 1

    # After 5 frames, finish the switch
    if switch_state["counter"] >= 5:
        tab_bar.enabled = True
        switch_state["active"] = False
        print(f"Switch complete to {tabs[target_idx].label}")

    C.viewport.wake()


C.viewport.wait_for_input = False

C.viewport.handlers += [
    dcg.KeyPressHandler(C, key=dcg.Key.TAB, callback=cycle_tabs),
    dcg.RenderHandler(C, callback=on_frame_render)
]

C.viewport.initialize()
loop = asyncio.new_event_loop()
while C.running:
    loop.run_until_complete(run_viewport_loop(C.viewport))
