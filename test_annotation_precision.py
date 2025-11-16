#!/usr/bin/env python3
"""
Minimal example demonstrating Float32 precision issue with draggable annotations.

This script creates a plot with large x-axis values (around 1,000,000) and a
draggable annotation. Before the fix, dragging the annotation would show
quantized movement with jumps of 128, 256, etc. due to Float32 precision loss.

After the fix, the annotation should move smoothly.
"""

import dearcygui as dcg

# Track annotation position for debugging
annotation_x = 1_000_000.0
annotation_y = 50.0


def on_dragging(handler, target, drag_deltas):
    """Called continuously while dragging the annotation."""
    global annotation_x, annotation_y

    # This is what happens in draggable annotations
    # Before fix: drag_deltas are Float32, causing precision loss at large values
    # After fix: drag_deltas maintain better precision
    annotation_x = handler.user_data['backup_x'] + drag_deltas[0]
    annotation_y = handler.user_data['backup_y'] + drag_deltas[1]

    # Update the annotation position
    handler.user_data['annotation'].x = annotation_x
    handler.user_data['annotation'].y = annotation_y

    # Print to show precision - before fix you'd see jumps like 128, 256
    print(f"Position: x={annotation_x:.2f}, y={annotation_y:.2f}, delta_x={drag_deltas[0]:.6f}, delta_y={drag_deltas[1]:.6f}")


def on_clicked(handler, target):
    """Called when starting to drag - backup the current position."""
    annotation = handler.user_data['annotation']
    handler.user_data['backup_x'] = annotation.x
    handler.user_data['backup_y'] = annotation.y
    print(f"\nStarted dragging from: x={annotation.x:.2f}, y={annotation.y:.2f}")


def main():
    # Create context and viewport
    context = dcg.Context()

    with dcg.Window(context=context, label="Annotation Precision Test", width=800, height=600) as window:
        with dcg.Plot(context=context, label="Precision Test Plot", height=-1, width=-1) as plot:
            # Set large x-axis range to demonstrate precision issue
            dcg.PlotAxisConfig(context=context, axis=dcg.Axis.X1, limits=(999_000, 1_001_000))
            dcg.PlotAxisConfig(context=context, axis=dcg.Axis.Y1, limits=(0, 100))

            # Create an annotation at a large x-coordinate
            annotation = dcg.PlotAnnotation(
                context=context,
                parent=plot,
                x=annotation_x,
                y=annotation_y,
                text="Drag me!",
                offset=(10, 10)
            )

            # Create an invisible button for dragging
            button = dcg.DrawInvisibleButton(
                context=context,
                parent=plot,
                p1=(annotation_x - 50, annotation_y - 5),
                p2=(annotation_x + 50, annotation_y + 5)
            )

            # Setup dragging handlers
            clicked_handler = dcg.ClickedHandler(
                context=context,
                parent=button,
                callback=on_clicked
            )
            clicked_handler.user_data = {'annotation': annotation}

            dragging_handler = dcg.DraggingHandler(
                context=context,
                parent=button,
                callback=on_dragging
            )
            dragging_handler.user_data = {
                'annotation': annotation,
                'backup_x': annotation_x,
                'backup_y': annotation_y
            }

            # Add a line to show the scale
            dcg.PlotLine(
                context=context,
                parent=plot,
                x=[999_000, 1_001_000],
                y=[25, 25],
                label="Reference line"
            )

    # Setup viewport
    viewport = dcg.Viewport(context=context, title="Float32 Precision Issue Demo", width=800, height=600)
    viewport.initialize()

    print("=" * 70)
    print("Float32 Precision Test for Draggable Annotations")
    print("=" * 70)
    print("Instructions:")
    print("1. Try dragging the 'Drag me!' annotation left and right")
    print("2. Watch the console output for position changes")
    print("")
    print("BEFORE FIX:")
    print("  - You would see jumps of 128, 256, etc. in the x-coordinate")
    print("  - Movement would feel 'sticky' or quantized")
    print("")
    print("AFTER FIX:")
    print("  - Smooth movement with precise delta values")
    print("  - Position changes match mouse movement accurately")
    print("=" * 70)
    print("")

    # Run the application
    while viewport.running:
        context.viewport.render_frame()

    viewport.cleanup()


if __name__ == "__main__":
    main()
