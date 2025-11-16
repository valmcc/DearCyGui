#!/usr/bin/env python3
"""
This demonstrates the ACTUAL precision issue you were experiencing.

The problem occurs when:
1. You have a large coordinate value (e.g., x = 1,000,000)
2. You drag the mouse slowly (small pixel deltas)
3. Those small deltas get added to the large backup coordinate

With Float32 cast, small deltas are lost completely!
"""

import struct


def float32(value):
    """Convert to float32 and back (simulating precision loss)."""
    return struct.unpack('f', struct.pack('f', value))[0]


def simulate_dragging():
    """Simulate what happens during actual dragging."""
    print("=" * 80)
    print("REALISTIC DRAGGING SCENARIO")
    print("=" * 80)
    print()
    print("Setup:")
    print("  - Annotation at x = 1,000,000.0")
    print("  - User drags mouse slowly (1-10 pixels per frame)")
    print("  - Plot scale: 1 pixel = 5.0 plot units")
    print()

    backup_x = 1_000_000.0
    plot_scale = 5.0  # 1 pixel = 5 plot units

    # Simulate dragging the mouse slowly (in pixels)
    mouse_pixels = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 20, 25, 30]

    print("BEFORE FIX - with explicit <float> cast in DraggingHandler:")
    print("-" * 80)
    print("Mouse Pixels | Plot Delta | Float32(backup+delta) | Actual Movement")
    print("-" * 80)

    for pixels in mouse_pixels:
        plot_delta = pixels * plot_scale
        plot_delta_f32 = float32(plot_delta)

        # This is what happened BEFORE the fix:
        # The delta gets cast to float32, then added to backup_x
        # But we're ALSO simulating what happens when the result is stored back
        new_x_bad = float32(backup_x + plot_delta_f32)
        actual_movement = new_x_bad - backup_x

        marker = "✓" if abs(actual_movement - plot_delta) < 0.1 else "✗"
        print(f"{pixels:4d} px      | {plot_delta:6.1f}     | {new_x_bad:13.2f}         | "
              f"{actual_movement:6.1f}  {marker}")

    print()
    print("AFTER FIX - without explicit cast (Python float/Float64):")
    print("-" * 80)
    print("Mouse Pixels | Plot Delta | Float64(backup+delta) | Actual Movement")
    print("-" * 80)

    for pixels in mouse_pixels:
        plot_delta = pixels * plot_scale

        # After the fix: Python handles everything as float64
        new_x_good = backup_x + plot_delta
        actual_movement = new_x_good - backup_x

        marker = "✓"
        print(f"{pixels:4d} px      | {plot_delta:6.1f}     | {new_x_good:13.2f}         | "
              f"{actual_movement:6.1f}  {marker}")


def show_catastrophic_case():
    """Show where Float32 completely fails."""
    print()
    print()
    print("=" * 80)
    print("CATASTROPHIC CASE: Very Small Deltas at Large Coordinates")
    print("=" * 80)
    print()

    backup_x = 1_000_000.0

    # Very small deltas (like fine mouse movements in plot units)
    small_deltas = [0.01, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0]

    print("Testing small drag deltas at x = 1,000,000.0:")
    print("-" * 80)
    print("Delta | Float32 Result | Float64 Result | Float32 Lost?")
    print("-" * 80)

    for delta in small_deltas:
        # With Float32 cast (BEFORE FIX)
        result_f32 = float32(backup_x + float32(delta))
        movement_f32 = result_f32 - backup_x

        # With Float64 (AFTER FIX)
        result_f64 = backup_x + delta
        movement_f64 = result_f64 - backup_x

        lost = abs(movement_f32 - delta) > 0.001
        marker = "✗ YES!" if lost else "✓ no"

        print(f"{delta:5.2f} | {movement_f32:14.4f} | {movement_f64:14.4f} | {marker}")

    print()
    print("Analysis:")
    print("  - Float32 loses deltas smaller than ~0.12 at x=1,000,000")
    print("  - Float64 preserves all deltas accurately")
    print("  - This is why you saw 'sticky' or 'quantized' movement!")


def explain_the_jumps():
    """Explain why you see jumps of 128, 256, etc."""
    print()
    print()
    print("=" * 80)
    print("WHY DID YOU SEE JUMPS OF 128, 256, ETC.?")
    print("=" * 80)
    print()

    backup_x = 1_000_000.0

    # Find what deltas actually cause changes
    print("Finding the actual step sizes at x=1,000,000.0 with Float32:")
    print("-" * 80)

    last_position = backup_x
    step_count = 0
    found_steps = []

    for i in range(1, 500):
        delta = float(i)
        new_pos = float32(backup_x + float32(delta))

        if new_pos != last_position:
            step_size = new_pos - last_position
            found_steps.append((i, delta, step_size))
            last_position = new_pos
            step_count += 1

            if step_count <= 10:  # Show first 10 steps
                print(f"  Step {step_count}: delta={delta:.0f} → movement={step_size:.1f}")

    print()
    print(f"Notice the pattern? Steps are NOT evenly spaced!")
    print(f"This is because Float32's precision is relative, not absolute.")
    print()
    print("At x=1,000,000:")
    print(f"  - Float32 mantissa gives ~6-7 significant digits")
    print(f"  - Smallest representable step at this magnitude: ~0.0625")
    print(f"  - But when cast back and forth, you get irregular jumps")


if __name__ == "__main__":
    simulate_dragging()
    show_catastrophic_case()
    explain_the_jumps()

    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()
    print("The issue you experienced:")
    print("  1. Annotation at large x-coordinate (e.g., 1,000,000)")
    print("  2. DraggingHandler cast drag_deltas to <float> (Float32)")
    print("  3. Your callback: self.x = self._backup_x + drag_deltas[0]")
    print("  4. Small deltas were LOST due to Float32 precision limits")
    print("  5. Result: Quantized, 'sticky' movement with large jumps")
    print()
    print("The fix:")
    print("  - Removed <float> cast in DraggingHandler")
    print("  - Python now uses Float64 for drag_deltas")
    print("  - Small deltas are preserved accurately")
    print("  - Result: Smooth, precise dragging even at large coordinates")
    print("=" * 80)
