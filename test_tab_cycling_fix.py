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


# Track pending tab switch
pending_switch = {"target_idx": None, "frames_remaining": 0}


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

    # Disable all plots to prevent mouse interference
    all_plots = []
    for tab in tabs:
        for child in tab.children:
            if isinstance(child, dcg.Plot):
                all_plots.append(child)
                child.enabled = False

    # Schedule the tab switch to persist for multiple frames
    pending_switch["target_idx"] = next_idx
    pending_switch["frames_remaining"] = 3  # Keep setting for 3 frames
    pending_switch["plots"] = all_plots

    # Immediately set the value
    tabs[next_idx].value = True
    C.viewport.wake()


def on_frame_render(s, t, d):
    """Called every frame to ensure tab switch persists."""
    if pending_switch["target_idx"] is not None:
        tabs = [c for c in tab_bar.children if isinstance(c, dcg.Tab)]
        target_idx = pending_switch["target_idx"]

        # Keep setting the value
        tabs[target_idx].value = True

        pending_switch["frames_remaining"] -= 1

        # After frames are done, re-enable plots
        if pending_switch["frames_remaining"] <= 0:
            for plot in pending_switch.get("plots", []):
                plot.enabled = True
            pending_switch["target_idx"] = None
            pending_switch["plots"] = []
            print(f"Tab switch complete, plots re-enabled")

        C.viewport.wake()


C.viewport.wait_for_input = False

C.viewport.handlers += [
    dcg.KeyPressHandler(C, key=dcg.Key.TAB, callback=cycle_tabs),
    dcg.RenderHandler(C, callback=on_frame_render)  # Called every frame
]

C.viewport.initialize()
loop = asyncio.new_event_loop()
while C.running:
    loop.run_until_complete(run_viewport_loop(C.viewport))
