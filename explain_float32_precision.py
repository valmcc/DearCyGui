#!/usr/bin/env python3
"""
Mathematical demonstration of Float32 vs Float64 precision issue.

This shows why the explicit <float> cast in DraggingHandler caused
quantized movement at large coordinate values.
"""

import struct


def float32(value):
    """Convert a value to float32 and back to float64 (simulating precision loss)."""
    return struct.unpack('f', struct.pack('f', value))[0]


def demonstrate_precision_loss():
    print("=" * 80)
    print("Float32 vs Float64 Precision at Large Values")
    print("=" * 80)
    print()

    # Simulate what happens when dragging an annotation at x=1,000,000
    base_position = 1_000_000.0

    print(f"Starting position: {base_position}")
    print()
    print("Scenario: User drags mouse slowly to the right (1 pixel at a time)")
    print("-" * 80)
    print()

    # Simulate small drag deltas (mouse movements)
    drag_deltas_to_test = [0.5, 1.0, 2.0, 5.0, 10.0, 50.0, 100.0, 128.0]

    print("BEFORE FIX (with explicit <float> cast):")
    print("-" * 80)
    for delta in drag_deltas_to_test:
        # This is what happened before the fix:
        # drag_deltas were cast to float32
        delta_float32 = float32(delta)

        # Then added to the base position (which gets converted to float32 in the process)
        new_pos_bad = float32(float32(base_position) + delta_float32)
        actual_movement = new_pos_bad - base_position

        print(f"  Delta={delta:6.1f} → "
              f"float32({base_position}) + float32({delta}) = {new_pos_bad:.2f} → "
              f"Actual movement: {actual_movement:+.2f}")

    print()
    print("AFTER FIX (without explicit cast, using Python float/Float64):")
    print("-" * 80)
    for delta in drag_deltas_to_test:
        # After the fix: drag_deltas stay as they are
        # Python automatically handles them as float64
        new_pos_good = base_position + delta
        actual_movement = new_pos_good - base_position

        print(f"  Delta={delta:6.1f} → "
              f"{base_position} + {delta} = {new_pos_good:.2f} → "
              f"Actual movement: {actual_movement:+.2f}")

    print()
    print("=" * 80)
    print("ANALYSIS:")
    print("=" * 80)
    print()
    print("Float32 has ~7 decimal digits of precision.")
    print(f"At x=1,000,000 (7 digits), the precision is approximately:")
    print(f"  ±{2**(-23) * 1_000_000:.2f} units")
    print()
    print("This means:")
    print("  - Deltas smaller than ~0.12 are completely lost")
    print("  - Movement appears 'quantized' in steps of ~0.12")
    print("  - At pixel-to-plot scales, this becomes jumps of 128+ plot units")
    print()
    print("Float64 has ~16 decimal digits of precision.")
    print(f"At x=1,000,000, the precision is approximately:")
    print(f"  ±{2**(-52) * 1_000_000:.10f} units")
    print()
    print("This is sufficient for smooth dragging even at very large coordinates!")
    print()


def show_quantization_effect():
    """Show the 'sticky' effect at different coordinate ranges."""
    print("=" * 80)
    print("Quantization Effect at Different Coordinate Ranges")
    print("=" * 80)
    print()

    test_positions = [100.0, 10_000.0, 100_000.0, 1_000_000.0, 10_000_000.0]

    for base_pos in test_positions:
        print(f"\nAt x = {base_pos:,.0f}:")
        print("-" * 40)

        # Try adding small increments
        unique_positions = set()
        for i in range(256):
            delta = i * 0.5  # Try to move in 0.5 unit increments
            new_pos = float32(float32(base_pos) + float32(delta))
            unique_positions.add(new_pos)

        # Check the minimum non-zero step
        sorted_positions = sorted(unique_positions)
        if len(sorted_positions) > 1:
            min_step = sorted_positions[1] - sorted_positions[0]
            print(f"  Minimum step size (Float32): {min_step:.2f} units")
            print(f"  Number of distinct positions in 128 units: {len(unique_positions)}")
            if min_step > 1.0:
                print(f"  ⚠️  WARNING: Positions will jump by {min_step:.0f} units!")


if __name__ == "__main__":
    demonstrate_precision_loss()
    print("\n\n")
    show_quantization_effect()

    print()
    print("=" * 80)
    print("CONCLUSION:")
    print("=" * 80)
    print()
    print("The explicit <float> cast in DraggingHandler caused precision loss")
    print("when dragging annotations/points at large coordinate values.")
    print()
    print("By removing the cast and letting Python handle the conversion,")
    print("we maintain Float64 precision throughout the calculation:")
    print("  new_x = backup_x + drag_delta")
    print()
    print("This allows smooth dragging even at coordinates like 1,000,000+")
    print("=" * 80)
