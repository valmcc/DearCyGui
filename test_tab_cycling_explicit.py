import dearcygui as dcg
import asyncio
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


# Track the switch
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

    # Start the forced switch
    switch_state["target_idx"] = next_idx
    switch_state["counter"] = 10  # Force for 10 frames

    # Immediately set ALL tab values explicitly
    for i, tab in enumerate(tabs):
        tab.value = (i == next_idx)

    C.viewport.wake()


def on_render(s, t, d):
    """Called every frame on the viewport (before children render)."""
    if switch_state["counter"] > 0:
        tabs = [c for c in tab_bar.children if isinstance(c, dcg.Tab)]
        target_idx = switch_state["target_idx"]

        # Explicitly set ALL tab values
        for i, tab in enumerate(tabs):
            tab.value = (i == target_idx)

        switch_state["counter"] -= 1

        if switch_state["counter"] == 0:
            # Verify
            actually_active = None
            for i, tab in enumerate(tabs):
                if tab.value:
                    actually_active = i
                    break
            print(f"Switch ended. Target: {tabs[target_idx].label}, Actually active: {tabs[actually_active].label if actually_active is not None else 'NONE'}")

        C.viewport.wake()


C.viewport.wait_for_input = False

C.viewport.handlers += [
    dcg.KeyPressHandler(C, key=dcg.Key.TAB, callback=cycle_tabs),
]

# Add render handler to the WINDOW, not viewport, so it runs before tab bar
window.handlers += [
    dcg.RenderHandler(C, callback=on_render)
]

C.viewport.initialize()
loop = asyncio.new_event_loop()
while C.running:
    loop.run_until_complete(run_viewport_loop(C.viewport))
