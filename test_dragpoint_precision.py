#!/usr/bin/env python3
"""
Simpler example using built-in DragPoint to show Float32 precision issue.

This demonstrates the precision problem with draggable points at large x-values.
The DragPoint class uses DraggingHandler internally, so it's affected by the
same Float32 precision issue.
"""

import dearcygui as dcg
from dearcygui.utils.draw_draggable import DragPoint


def on_dragging(sender, target):
    """Called while dragging - print current position."""
    point = sender.user_data['point']
    print(f"Dragging - x={point.x:.2f}, y={point.y:.2f}")


def main():
    context = dcg.Context()

    with dcg.Window(context=context, label="DragPoint Precision Test", width=1000, height=600) as window:
        with dcg.Plot(context=context, label="Float32 Precision Test", height=-1, width=-1) as plot:
            # Set large x-axis range - this is where Float32 precision breaks down
            dcg.PlotAxisConfig(context=context, axis=dcg.Axis.X1, limits=(999_900, 1_000_100))
            dcg.PlotAxisConfig(context=context, axis=dcg.Axis.Y1, limits=(0, 100))

            # Create draggable points at different x-coordinates
            # Point 1: At a small x-value (good precision)
            point_small = DragPoint(
                context=context,
                parent=plot,
                x=1_000.0,
                y=50.0,
                radius=5,
                color=(0, 255, 0, 255),
                label="Small X (good precision)"
            )

            # Point 2: At a large x-value (bad precision with Float32)
            point_large = DragPoint(
                context=context,
                parent=plot,
                x=1_000_000.0,
                y=50.0,
                radius=5,
                color=(255, 0, 0, 255),
                label="Large X (precision issue)"
            )

            # Add text annotations to explain
            dcg.PlotAnnotation(
                context=context,
                parent=plot,
                x=1_000_000.0,
                y=70.0,
                text="← Drag this red point",
                offset=(10, -30)
            )

            # Add a reference grid
            for i in range(999_900, 1_000_100, 20):
                dcg.PlotLine(
                    context=context,
                    parent=plot,
                    x=[i, i],
                    y=[0, 100],
                    color=(128, 128, 128, 100)
                )

    viewport = dcg.Viewport(context=context, title="DragPoint Float32 Precision Demo", width=1000, height=600)
    viewport.initialize()

    print("=" * 80)
    print("Float32 Precision Test - DragPoint at Large Coordinates")
    print("=" * 80)
    print("")
    print("SETUP:")
    print(f"  - Red point at x={point_large.x:.1f} (large value)")
    print(f"  - Green point at x={point_small.x:.1f} (small value)")
    print("")
    print("EXPERIMENT:")
    print("  1. Drag the GREEN point (small x-value) - should move smoothly")
    print("  2. Now drag the RED point (large x-value) left/right")
    print("")
    print("BEFORE FIX (with Float32 explicit cast):")
    print("  - Red point shows 'sticky' movement")
    print("  - Position jumps in increments of ~128 units")
    print("  - This is because Float32 has ~6-7 digits of precision:")
    print("    At x=1,000,000, the precision is about ±0.12")
    print("    When cast to Float32: 1000000 + 0.5 → 1000000 (lost!)")
    print("")
    print("AFTER FIX (without explicit Float32 cast):")
    print("  - Red point moves smoothly")
    print("  - Python's float (Float64) maintains precision")
    print("  - Float64 has ~15-16 digits, so at x=1,000,000:")
    print("    precision is about ±0.00000001 (much better)")
    print("")
    print("=" * 80)
    print("\nWatch the console - position updates will show when you drag:\n")

    # Add callbacks to monitor dragging
    with point_large._invisible:
        dcg.DraggingHandler(context=context, callback=lambda h, t, d:
            print(f"  Red point delta: ({d[0]:+.6f}, {d[1]:+.6f}) -> x={point_large.x:.2f}"))

    with point_small._invisible:
        dcg.DraggingHandler(context=context, callback=lambda h, t, d:
            print(f"  Green point delta: ({d[0]:+.6f}, {d[1]:+.6f}) -> x={point_small.x:.2f}"))

    # Run the application
    while viewport.running:
        context.viewport.render_frame()

    viewport.cleanup()


if __name__ == "__main__":
    main()
