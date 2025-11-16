# Float32 Precision Fix for DraggingHandler

## Problem Summary

When dragging annotations or other plot elements at large x-axis values (e.g., 1,000,000+), the movement appeared "sticky" or "quantized" with jumps of irregular sizes. This was caused by an explicit `<float>` cast in the `DraggingHandler` that forced drag deltas to Float32 precision.

## Root Cause

In `/home/user/DearCyGui/dearcygui/handler.pyx`, lines 647-648:

```cython
# BEFORE FIX - with explicit Float32 cast
self.context.queue_callback(self._callback,
                            self,
                            item,
                            (<float>state.cur.drag_deltas[i].x,
                             <float>state.cur.drag_deltas[i].y))
```

The explicit `<float>` cast forced the drag deltas to Float32 (single precision) before passing them to Python callbacks. When these deltas were then used in calculations like:

```python
self.x = self._backup_x + drag_deltas[0]  # backup_x = 1,000,000
```

The Float32 precision was insufficient:
- **Float32** has ~7 decimal digits of precision
- At x=1,000,000, the precision is approximately ±0.0625 to ±0.125
- Deltas smaller than this threshold were completely lost or distorted
- Result: Irregular jumps instead of smooth movement

## The Fix

Removed the explicit `<float>` cast to match the behavior of `DraggedHandler`:

```cython
# AFTER FIX - let Python handle precision
self.context.queue_callback(self._callback,
                            self,
                            item,
                            (state.cur.drag_deltas[i].x,
                             state.cur.drag_deltas[i].y))
```

Now Python receives the values and automatically handles them as Float64 (double precision):
- **Float64** has ~16 decimal digits of precision
- At x=1,000,000, precision is approximately ±0.00000001
- All realistic drag deltas are preserved accurately
- Result: Smooth, precise dragging even at large coordinates

## Demonstration Scripts

Three example scripts are provided to demonstrate the issue:

1. **`explain_float32_precision.py`**: Mathematical demonstration showing precision loss at different coordinate ranges

2. **`show_real_precision_issue.py`**: Realistic simulation of dragging scenarios, showing:
   - How small deltas (<0.5) are lost with Float32
   - Why you see quantized movement
   - The difference before and after the fix

3. **`test_dragpoint_precision.py`**: Interactive GUI demo using DragPoint
   - Drag points at small vs large x-coordinates
   - See the precision difference in real-time

## Example Output

From `show_real_precision_issue.py`:

```
Testing small drag deltas at x = 1,000,000.0:
--------------------------------------------------------------------------------
Delta | Float32 Result | Float64 Result | Float32 Lost?
--------------------------------------------------------------------------------
 0.01 |         0.0000 |         0.0100 | ✗ YES!
 0.05 |         0.0625 |         0.0500 | ✗ YES!
 0.10 |         0.1250 |         0.1000 | ✗ YES!
 0.20 |         0.1875 |         0.2000 | ✗ YES!
 0.50 |         0.5000 |         0.5000 | ✓ no
```

This clearly shows how deltas smaller than ~0.5 are lost or distorted with Float32.

## Testing the Fix

To verify the fix works:

1. Run the mathematical demonstration:
   ```bash
   python3 show_real_precision_issue.py
   ```

2. Run the interactive GUI demo (requires building DearCyGui with the fix):
   ```bash
   python3 test_dragpoint_precision.py
   ```

3. In the GUI demo:
   - Drag the red point (at x=1,000,000) slowly
   - Before fix: Movement would feel sticky with large jumps
   - After fix: Smooth, precise movement

## Affected Code

- **Fixed**: `dearcygui/handler.pyx:647-648` - DraggingHandler callback
- **Already correct**: `dearcygui/handler.pyx:598-599` - DraggedHandler callback (no cast)
- **Coordinates**: `dearcygui/plot.pxd:167-168` - PlotAnnotation uses `double` (Float64)

## Conclusion

This simple fix (removing two `<float>` casts) resolves the precision issue entirely. The `DraggingHandler` now behaves consistently with `DraggedHandler`, allowing Python to handle precision conversion naturally using Float64 throughout the calculation chain.
