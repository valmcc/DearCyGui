# DearCyGui Handlers Documentation

## Table of Contents

- [Overview](#overview)
- [Basic Concepts](#basic-concepts)
- [Handler Types](#handler-types)
  - [Base & Container Handlers](#base--container-handlers)
  - [Item State Handlers](#item-state-handlers)
  - [Click & Interaction Handlers](#click--interaction-handlers)
  - [Focus Handlers](#focus-handlers)
  - [Hover Handlers](#hover-handlers)
  - [Position & Size Handlers](#position--size-handlers)
  - [Toggle & Expand Handlers](#toggle--expand-handlers)
  - [Render Handlers](#render-handlers)
  - [Mouse Cursor Handler](#mouse-cursor-handler)
  - [Global Keyboard Handlers](#global-keyboard-handlers)
  - [Global Mouse Handlers](#global-mouse-handlers)
  - [Drag & Drop Handlers](#drag--drop-handlers)
- [Component Compatibility](#component-compatibility)
- [Usage Patterns](#usage-patterns)
- [Advanced Topics](#advanced-topics)
- [Common Use Cases](#common-use-cases)

---

## Overview

**Handlers** in DearCyGui are objects that monitor item states and trigger callbacks when specific conditions are met. They provide a declarative, event-driven approach to building interactive UIs without manual state checking in your application loop.

### Key Benefits

- **Declarative**: Attach handlers to items to define what happens on events
- **Composable**: Multiple handlers can be attached to a single item
- **Flexible**: Combine handlers with logical operations for complex conditions
- **Performant**: Handlers only run when items are rendered
- **Thread-safe**: All handler operations are mutex-protected

### Basic Usage

```python
import dearcygui as dcg

C = dcg.Context()

# Create a button
button = dcg.Button(C, label="Click me!")

# Attach a click handler
handler = dcg.ClickedHandler(C, callback=lambda s, t, d: print("Button clicked!"))
button.handlers += [handler]

# Attach multiple handlers
button.handlers += [
    dcg.HoverHandler(C, callback=lambda s,t,d: print("Hovering")),
    dcg.DoubleClickedHandler(C, callback=lambda s,t,d: print("Double clicked"))
]
```

---

## Basic Concepts

### Handler Lifecycle

1. **Creation**: Handler is created with `HandlerType(context, callback=...)`
2. **Attachment**: Handler is added to an item via `item.handlers += [handler]`
3. **Binding Check**: Handler checks if it can bind to the item (based on capabilities)
4. **Execution**: Every frame, handler checks its condition and triggers callback if met
5. **Cleanup**: Handler is removed when item is destroyed or explicitly cleared

### Callback Signature

All handler callbacks receive three arguments:

```python
def callback(sender, target, data):
    """
    sender: The handler object that triggered
    target: The item the handler is attached to
    data: Handler-specific data (None, int, tuple, etc.)
    """
    pass
```

### Handler Capabilities

Handlers check item "capabilities" to determine if they can attach. For example:
- `ClickedHandler` requires `can_be_clicked` capability
- `HoverHandler` requires `can_be_hovered` capability
- Global handlers (keyboard, mouse) can attach to any rendered item

---

## Handler Types

### Base & Container Handlers

#### CustomHandler

**Purpose**: Base class for creating custom handlers with Python logic.

**Usage**: Subclass and implement `check_can_bind()` and `check_status()` methods.

**Properties**: None (defined in subclass)

**Callback Data**: None (defined in subclass)

**Example**:
```python
class InGrabAreaHandler(dcg.CustomHandler):
    def check_can_bind(self, item):
        # Return True if handler can bind to this item type
        return isinstance(item, DraggableBar)

    def check_status(self, item):
        # Return True when condition is met
        return item._is_in_grab_area()

    def run(self, item):
        # Optional: implement custom action instead of callback
        print(f"In grab area of {item}")
```

**Use Cases**:
- Custom state checking logic
- Specialized interaction patterns
- Domain-specific condition monitoring

**Performance Note**: Called every frame in Python, use sparingly for expensive operations.

---

#### HandlerList

**Purpose**: Container for multiple handlers with logical operations (AND/OR/NONE).

**Usage**: Group handlers and execute callback based on combined states.

**Properties**:
- `op`: `HandlerListOP.ALL` (AND), `HandlerListOP.ANY` (OR), or `HandlerListOP.NONE` (NOT)

**Callback Data**: None

**Example**:
```python
# Trigger when hovering AND holding Ctrl key
with dcg.HandlerList(C, op=dcg.HandlerListOP.ALL,
                     callback=do_something) as combo:
    dcg.HoverHandler(C)
    dcg.KeyDownHandler(C, key=dcg.Key.CTRL)

button.handlers += [combo]
```

**Use Cases**:
- Keyboard shortcuts with modifiers (Ctrl+Click)
- Complex multi-condition interactions
- Combining hover + click + key states

---

#### ConditionalHandler

**Purpose**: Execute first child handler only when all other child handlers' conditions are met.

**Usage**: Conditionally run handlers based on other handler states.

**Properties**: None

**Callback Data**: Passes through from first child handler

**Example**:
```python
# Change cursor to hand only when hovering AND Shift key is down
with dcg.ConditionalHandler(C) as conditional:
    # First child - the action to perform
    dcg.MouseCursorHandler(C, cursor=dcg.MouseCursor.HAND)
    # Other children - conditions that must be met
    dcg.HoverHandler(C)
    dcg.KeyDownHandler(C, key=dcg.Key.SHIFT)

button.handlers += [conditional]
```

**Use Cases**:
- Skip expensive operations when preconditions aren't met
- Context-sensitive cursor changes
- Conditional visual feedback

**Note**: The first child handler runs when all other children's conditions are True.

---

#### OtherItemHandler

**Purpose**: Monitor states from a different item than the one the handler is attached to.

**Usage**: Check conditions on one item while attached to another.

**Properties**:
- `target`: The item to monitor (different from attached item)

**Callback Data**: None

**Example**:
```python
# Monitor slider value from button handler
slider = dcg.Slider(C, min_value=0, max_value=100)
button = dcg.Button(C, label="Watch slider")

other_handler = dcg.OtherItemHandler(C, target=slider)
# Add child handler that checks slider's state
other_handler.handlers += [dcg.EditedHandler(C, callback=on_slider_change)]

button.handlers += [other_handler]
```

**Use Cases**:
- Creating dependencies between interface elements
- Monitoring one widget while interacting with another
- Cross-widget validation

---

#### BoolHandler

**Purpose**: Fit a SharedBool condition inside a handler tree.

**Usage**: Use external boolean conditions in handler compositions.

**Properties**:
- `condition`: `SharedBool` object

**Callback Data**: None

**Example**:
```python
enabled_condition = dcg.SharedBool(C, value=True)

# Only process click when condition is True
with dcg.HandlerList(C, op=dcg.HandlerListOP.ALL, callback=do_action) as combo:
    dcg.ClickedHandler(C)
    dcg.BoolHandler(C, condition=enabled_condition)

button.handlers += [combo]

# Toggle condition from elsewhere
enabled_condition.value = False  # Disable click handling
```

**Use Cases**:
- Enable/disable handler groups without removing them
- External state control over handler execution
- Feature flags in handler trees

---

### Item State Handlers

#### ActivatedHandler

**Purpose**: Triggers when item transitions from non-active to active state.

**Requirement**: `can_be_active` capability

**Properties**: None

**Callback Data**: None

**Example**:
```python
button = dcg.Button(C, label="Press me")
button.handlers += [
    dcg.ActivatedHandler(C, callback=lambda s,t,d: print("Button pressed!"))
]
```

**Use Cases**:
- Button press detection (initial press only)
- Detecting when widget becomes interacted with
- Triggering one-time actions on activation

**Compatible Components**: Buttons, Checkboxes, Radio buttons, Selectable items

---

#### ActiveHandler

**Purpose**: Triggers continuously while item is in active state (e.g., button held down).

**Requirement**: `can_be_active` capability

**Properties**: None

**Callback Data**: None

**Example**:
```python
button = dcg.Button(C, label="Hold me")
button.handlers += [
    dcg.ActiveHandler(C, callback=lambda s,t,d: print("Holding..."))
]
```

**Use Cases**:
- Continuous actions while button is held
- Real-time state monitoring during interaction
- Hold-to-repeat functionality

**Compatible Components**: Buttons, Checkboxes, Radio buttons, Selectable items

---

#### DeactivatedHandler

**Purpose**: Triggers when active item loses activation.

**Requirement**: `can_be_active` capability

**Properties**: None

**Callback Data**: None

**Example**:
```python
button = dcg.Button(C, label="Release me")
button.handlers += [
    dcg.DeactivatedHandler(C, callback=lambda s,t,d: print("Released!"))
]
```

**Use Cases**:
- Button release detection
- Completing drag operations
- Cleanup after interaction ends

**Compatible Components**: Buttons, Checkboxes, Radio buttons, Selectable items

---

#### DeactivatedAfterEditHandler

**Purpose**: Triggers when editable item loses activation specifically after being edited.

**Requirement**: `can_be_deactivated_after_edited` capability

**Properties**: None

**Callback Data**: None

**Example**:
```python
input_field = dcg.InputText(C, label="Name")
input_field.handlers += [
    dcg.DeactivatedAfterEditHandler(C,
        callback=lambda s,t,d: validate_input(t.value))
]
```

**Use Cases**:
- Input field validation after editing
- Saving data when user finishes editing
- Committing changes only after edits

**Compatible Components**: InputText, InputInt, InputFloat, InputIntX, InputFloatX

**Note**: Only triggers if the value was actually changed, not just focused/unfocused.

---

#### EditedHandler

**Purpose**: Triggers on every frame when field value is changed.

**Requirement**: `can_be_edited` capability

**Properties**: None

**Callback Data**: None

**Example**:
```python
slider = dcg.SliderFloat(C, label="Volume")
slider.handlers += [
    dcg.EditedHandler(C, callback=lambda s,t,d: set_volume(t.value))
]
```

**Use Cases**:
- Real-time input validation
- Live preview of changes
- Immediate feedback on value changes

**Compatible Components**: All input widgets (InputText, Sliders, DragInt/Float, ColorEdit, etc.)

**Note**: Triggers continuously while editing, which can be expensive. Consider using `DeactivatedAfterEditHandler` for non-realtime updates.

---

### Click & Interaction Handlers

#### ClickedHandler

**Purpose**: Triggers when hovered item is clicked with specified mouse button.

**Requirement**: `can_be_clicked` capability

**Properties**:
- `button`: `dcg.MouseButton.LEFT` (default), `RIGHT`, `MIDDLE`, `X1`, `X2`

**Callback Data**: `button` (int) - The mouse button that was clicked

**Example**:
```python
item = dcg.Button(C, label="Click me")

# Left click
item.handlers += [
    dcg.ClickedHandler(C, button=dcg.MouseButton.LEFT,
        callback=lambda s,t,d: print("Left clicked"))
]

# Right click for context menu
item.handlers += [
    dcg.ClickedHandler(C, button=dcg.MouseButton.RIGHT,
        callback=lambda s,t,d: show_context_menu())
]
```

**Use Cases**:
- Button actions
- Menu item selection
- Context menus (right-click)
- Custom mouse button handling

**Compatible Components**: Most visible widgets (Buttons, Text, Images, DrawNodes, etc.)

---

#### DoubleClickedHandler

**Purpose**: Triggers on double-click with specified mouse button.

**Requirement**: `can_be_clicked` capability

**Properties**:
- `button`: `dcg.MouseButton` (default: LEFT)

**Callback Data**: `button` (int)

**Example**:
```python
list_item = dcg.Selectable(C, label="File.txt")
list_item.handlers += [
    dcg.DoubleClickedHandler(C,
        callback=lambda s,t,d: open_file(t.label))
]
```

**Use Cases**:
- Opening files/items in file browsers
- Entering edit mode
- Quick actions that differ from single click

**Compatible Components**: Most clickable widgets

**Note**: Double-click timing is controlled by ImGui's `io.MouseDoubleClickTime` setting.

---

#### DraggedHandler

**Purpose**: Triggers once when dragging ends (not continuously during drag).

**Requirement**: `can_be_dragged` capability

**Properties**:
- `button`: `dcg.MouseButton` (default: LEFT)

**Callback Data**: `(delta_x, delta_y)` tuple - Total drag distance

**Example**:
```python
node = dcg.DrawInWindow(C, button=True)
node.handlers += [
    dcg.DraggedHandler(C,
        callback=lambda s,t,(dx,dy): finalize_move(t, dx, dy))
]
```

**Use Cases**:
- Finalizing drag operations
- Committing position changes
- Undo/redo history for drags

**Compatible Components**: Widgets with drag capability (usually need `button=True`)

---

#### DraggingHandler

**Purpose**: Triggers every frame while item is being dragged.

**Requirement**: `can_be_dragged` capability

**Properties**:
- `button`: `dcg.MouseButton` (default: LEFT)

**Callback Data**: `(delta_x, delta_y)` tuple - Frame-by-frame delta

**Example**:
```python
draggable = dcg.DrawInWindow(C, button=True, x=100, y=100)
draggable.handlers += [
    dcg.DraggingHandler(C,
        callback=lambda s,t,(dx,dy): setattr(t, 'x', t.x + dx) or setattr(t, 'y', t.y + dy))
]
```

**Use Cases**:
- Real-time drag feedback
- Moving objects continuously
- Visual drag indicators

**Compatible Components**: Widgets with drag capability

**Performance Note**: Called every frame during drag, keep callback lightweight.

---

### Focus Handlers

#### FocusHandler

**Purpose**: Triggers continuously while item has keyboard focus.

**Requirement**: `can_be_focused` capability

**Properties**: None

**Callback Data**: None

**Example**:
```python
input_field = dcg.InputText(C, label="Username")
input_field.handlers += [
    dcg.FocusHandler(C, callback=lambda s,t,d: highlight_field(t))
]
```

**Use Cases**:
- Highlighting focused elements
- Continuous state while focused
- Focus-dependent visual effects

**Compatible Components**: Windows, Input widgets, Child windows

---

#### GotFocusHandler

**Purpose**: Triggers once when item gains keyboard focus.

**Requirement**: `can_be_focused` capability

**Properties**: None

**Callback Data**: None

**Example**:
```python
window = dcg.Window(C, label="Settings")
window.handlers += [
    dcg.GotFocusHandler(C, callback=lambda s,t,d: print(f"{t.label} focused"))
]
```

**Use Cases**:
- Initialize focus-dependent behavior
- Clear validation errors
- Start editing mode

**Compatible Components**: Windows, Input widgets, Child windows

---

#### LostFocusHandler

**Purpose**: Triggers once when item loses keyboard focus.

**Requirement**: `can_be_focused` capability

**Properties**: None

**Callback Data**: None

**Example**:
```python
input_field = dcg.InputText(C, label="Email")
input_field.handlers += [
    dcg.LostFocusHandler(C, callback=lambda s,t,d: validate_email(t.value))
]
```

**Use Cases**:
- Input validation on focus loss
- Saving data when moving to next field
- Cleanup focus-dependent state

**Compatible Components**: Windows, Input widgets, Child windows

---

### Hover Handlers

#### HoverHandler (Recommended)

**Purpose**: Triggers continuously while item is hovered by mouse.

**Requirement**: `can_be_hovered` capability

**Properties**: None

**Callback Data**: None

**Example**:
```python
button = dcg.Button(C, label="Hover me")
button.handlers += [
    dcg.HoverHandler(C, callback=lambda s,t,d: show_tooltip(t))
]
```

**Use Cases**:
- Showing tooltips
- Hover effects
- Cursor changes on hover

**Compatible Components**: Most visible widgets

**Note**: Prefer this over `MouseOverHandler` for general hover detection.

---

#### GotHoverHandler (Recommended)

**Purpose**: Triggers once when item becomes hovered.

**Requirement**: `can_be_hovered` capability

**Properties**: None

**Callback Data**: None

**Example**:
```python
button = dcg.Button(C, label="Info")
tooltip = dcg.Tooltip(C)
dcg.Text(C, value="This is a button", parent=tooltip)

button.handlers += [
    dcg.GotHoverHandler(C, callback=lambda s,t,d: setattr(tooltip, 'show', True))
]
```

**Use Cases**:
- Start animations
- Show tooltips
- Begin hover state

**Compatible Components**: Most visible widgets

---

#### LostHoverHandler (Recommended)

**Purpose**: Triggers once when item stops being hovered.

**Requirement**: `can_be_hovered` capability

**Properties**: None

**Callback Data**: None

**Example**:
```python
button.handlers += [
    dcg.LostHoverHandler(C, callback=lambda s,t,d: setattr(tooltip, 'show', False))
]
```

**Use Cases**:
- Hide tooltips
- Reset hover state
- End animations

**Compatible Components**: Most visible widgets

---

#### MouseOverHandler (Use with caution)

**Purpose**: Triggers when mouse is over item's rectangular bounds (pixel-based, not ImGui hover).

**Requirements**: `has_position` AND `has_rect_size` capabilities

**Properties**: None

**Callback Data**: None

**Example**:
```python
# For custom drag & drop with overlapping items
droppable = dcg.DrawInWindow(C, x=0, y=0, width=100, height=100)
droppable.handlers += [
    dcg.MouseOverHandler(C, callback=lambda s,t,d: highlight_drop_zone(t))
]
```

**Use Cases**:
- Custom drag & drop operations
- Pixel-perfect mouse detection
- Overlapping item interactions

**Compatible Components**: Items with position and size

**Note**: Differs from `HoverHandler` - this checks pixel bounds, while `HoverHandler` uses ImGui's hover logic (respects z-order, clipping, etc.). Prefer `HoverHandler` for most cases.

---

#### GotMouseOverHandler / LostMouseOverHandler

**Purpose**: Transition detection for `MouseOverHandler` state.

**Requirements**: `has_position` AND `has_rect_size` capabilities

**Properties**: None

**Callback Data**: None

**Use Cases**: Same as `MouseOverHandler` but for state transitions

---

### Position & Size Handlers

#### MotionHandler

**Purpose**: Triggers when item moves relative to specified positioning reference.

**Requirement**: `has_position` capability

**Properties**:
- `pos_policy`: Tuple of `dcg.Positioning` values
  - `dcg.Positioning.REL_PARENT` - Relative to parent
  - `dcg.Positioning.REL_WINDOW` - Relative to window
  - `dcg.Positioning.REL_VIEWPORT` - Relative to viewport

**Callback Data**: None

**Example**:
```python
moving_item = dcg.DrawInWindow(C, x=0, y=0)
moving_item.handlers += [
    dcg.MotionHandler(C,
        pos_policy=(dcg.Positioning.REL_PARENT,),
        callback=lambda s,t,d: print(f"Moved to ({t.x}, {t.y})"))
]
```

**Use Cases**:
- Tracking item movement
- Responding to layout changes
- Position-dependent logic

**Compatible Components**: All positioned items

---

#### ResizeHandler

**Purpose**: Triggers when item's bounding box changes size.

**Requirement**: `has_rect_size` capability

**Properties**: None

**Callback Data**: None

**Example**:
```python
window = dcg.Window(C, label="Resizable", resizable=True)
window.handlers += [
    dcg.ResizeHandler(C,
        callback=lambda s,t,d: adjust_layout(t.width, t.height))
]
```

**Use Cases**:
- Responsive layout adjustments
- Maintaining aspect ratios
- Size-dependent rendering

**Compatible Components**: All visible items with size

---

#### ContentResizeHandler

**Purpose**: Triggers when item's content region (inner area) changes size.

**Requirement**: `has_content_region` capability

**Properties**: None

**Callback Data**: None

**Example**:
```python
window = dcg.Window(C, label="Main", resizable=True)
window.handlers += [
    dcg.ContentResizeHandler(C,
        callback=lambda s,t,d: reflow_content(t))
]
```

**Use Cases**:
- Container resize handling
- Content reflow
- Scrollable area adjustments

**Compatible Components**: Windows, Child windows, Groups, Containers

---

### Toggle & Expand Handlers

#### ToggledOpenHandler

**Purpose**: Triggers when item transitions from closed to opened (collapsed to expanded).

**Requirement**: `can_be_toggled` capability

**Properties**: None

**Callback Data**: None

**Example**:
```python
tree_node = dcg.TreeNode(C, label="Folder")
tree_node.handlers += [
    dcg.ToggledOpenHandler(C,
        callback=lambda s,t,d: load_folder_contents(t))
]
```

**Use Cases**:
- Lazy-loading tree node contents
- Expanding animations
- Tracking expansion events

**Compatible Components**: TreeNode, CollapsingHeader

**Note**: "Open" refers to expanded state, NOT visibility or window open state.

---

#### ToggledCloseHandler

**Purpose**: Triggers when item transitions from opened to closed (expanded to collapsed).

**Requirement**: `can_be_toggled` capability

**Properties**: None

**Callback Data**: None

**Example**:
```python
tree_node = dcg.TreeNode(C, label="Folder")
tree_node.handlers += [
    dcg.ToggledCloseHandler(C,
        callback=lambda s,t,d: unload_folder_contents(t))
]
```

**Use Cases**:
- Cleanup on collapse
- Memory management
- Tracking collapse events

**Compatible Components**: TreeNode, CollapsingHeader

---

#### OpenHandler / CloseHandler

**Purpose**: Continuous state versions of toggled handlers. `OpenHandler` triggers while item is open, `CloseHandler` while closed.

**Requirement**: `can_be_toggled` capability

**Properties**: None

**Callback Data**: None

**Use Cases**:
- State-dependent rendering
- Continuous expanded/collapsed state monitoring

**Compatible Components**: TreeNode, CollapsingHeader

---

### Render Handlers

#### RenderHandler

**Purpose**: Triggers every frame when item is rendered.

**Requirement**: None (works on all rendered items)

**Properties**: None

**Callback Data**: None

**Example**:
```python
animated_item = dcg.Text(C, value="Loading")
animated_item.handlers += [
    dcg.RenderHandler(C, callback=lambda s,t,d: update_animation(t))
]
```

**Use Cases**:
- Per-frame updates
- Animations
- Real-time state polling

**Compatible Components**: All items

**Performance Warning**: Called every frame, keep callback extremely lightweight.

---

#### GotRenderHandler

**Purpose**: Triggers once when item starts being rendered (becomes visible).

**Requirement**: None

**Properties**: None

**Callback Data**: None

**Example**:
```python
widget = dcg.Button(C, label="Dynamic")
widget.handlers += [
    dcg.GotRenderHandler(C, callback=lambda s,t,d: initialize_widget(t))
]
```

**Use Cases**:
- Initialization when becoming visible
- Loading resources on demand
- Starting animations

**Compatible Components**: All items

---

#### LostRenderHandler

**Purpose**: Triggers once when item stops being rendered (becomes hidden).

**Requirement**: None

**Properties**: None

**Callback Data**: None

**Example**:
```python
tooltip = dcg.Tooltip(C)
tooltip.handlers += [
    dcg.LostRenderHandler(C, callback=lambda s,t,d: t.destroy())
]
```

**Use Cases**:
- Cleanup when hidden
- Unloading resources
- Destroying temporary items

**Compatible Components**: All items

**Note**: Handlers themselves don't run when item is not rendered, but this handler's callback executes on the transition to non-rendered state.

---

### Mouse Cursor Handler

#### MouseCursorHandler

**Purpose**: Changes mouse cursor appearance when handler condition is met.

**Requirement**: None

**Properties**:
- `cursor`: `dcg.MouseCursor` enum value
  - `ARROW` - Standard arrow
  - `TEXT_INPUT` - I-beam for text
  - `RESIZE_ALL` - Four-way arrows
  - `RESIZE_NS` - North-South resize
  - `RESIZE_EW` - East-West resize
  - `RESIZE_NESW` - Diagonal resize
  - `RESIZE_NWSE` - Diagonal resize
  - `HAND` - Pointing hand
  - `NOT_ALLOWED` - Prohibition sign

**Callback Data**: None (visual effect only)

**Example**:
```python
# Change cursor to hand when hovering
button = dcg.Button(C, label="Click")
with dcg.ConditionalHandler(C) as handler:
    dcg.MouseCursorHandler(C, cursor=dcg.MouseCursor.HAND)
    dcg.HoverHandler(C)
button.handlers += [handler]

# Show resize cursor in grab area
with dcg.ConditionalHandler(C) as handler:
    dcg.MouseCursorHandler(C, cursor=dcg.MouseCursor.RESIZE_EW)
    InGrabAreaHandler(C)  # Custom handler
    dcg.HoverHandler(C)
resizable_widget.handlers += [handler]
```

**Use Cases**:
- Context-sensitive cursor changes
- Visual feedback for draggable areas
- Indicating interactive regions

**Compatible Components**: Any item (usually combined with ConditionalHandler)

**Note**: Must be used within a handler tree (usually ConditionalHandler) to specify when the cursor change occurs.

---

### Global Keyboard Handlers

Global keyboard handlers monitor the entire keyboard state, not specific item states. They can be attached to any item but only execute when that item is rendered. Typically attached to the viewport for application-wide keyboard handling.

#### KeyDownHandler

**Purpose**: Triggers continuously while a specific key is held down.

**Requirement**: None (global handler)

**Properties**:
- `key`: `dcg.Key` enum value (e.g., `Key.A`, `Key.SPACE`, `Key.CTRL`)

**Callback Data**: `(key, duration)` tuple
- `key`: The key code (int)
- `duration`: How long the key has been held (seconds)

**Example**:
```python
# Attach to viewport for global key handling
C.viewport.handlers += [
    dcg.KeyDownHandler(C, key=dcg.Key.SPACE,
        callback=lambda s,t,(k,dur): player_jump())
]

# Hold to accelerate
C.viewport.handlers += [
    dcg.KeyDownHandler(C, key=dcg.Key.W,
        callback=lambda s,t,(k,dur): accelerate(dur))
]
```

**Use Cases**:
- Game controls (WASD movement)
- Continuous actions while key held
- Acceleration based on hold duration

---

#### KeyPressHandler

**Purpose**: Triggers once when a key is initially pressed.

**Requirement**: None (global handler)

**Properties**:
- `key`: `dcg.Key` enum value
- `repeat`: bool - If True, triggers repeatedly while held (like keyboard repeat)

**Callback Data**: `key` (int)

**Example**:
```python
# Global keyboard shortcuts
C.viewport.handlers += [
    dcg.KeyPressHandler(C, key=dcg.Key.ESCAPE,
        callback=lambda s,t,k: close_dialog()),
    dcg.KeyPressHandler(C, key=dcg.Key.F5,
        callback=lambda s,t,k: refresh_data())
]

# With repeat for scrolling
C.viewport.handlers += [
    dcg.KeyPressHandler(C, key=dcg.Key.DOWN_ARROW, repeat=True,
        callback=lambda s,t,k: scroll_down())
]
```

**Use Cases**:
- Keyboard shortcuts
- Menu hotkeys
- Single-press actions

---

#### KeyReleaseHandler

**Purpose**: Triggers once when a key is released.

**Requirement**: None (global handler)

**Properties**:
- `key`: `dcg.Key` enum value

**Callback Data**: `key` (int)

**Example**:
```python
C.viewport.handlers += [
    dcg.KeyReleaseHandler(C, key=dcg.Key.SPACE,
        callback=lambda s,t,k: player_stop_jump())
]
```

**Use Cases**:
- Detecting key release
- Stop continuous actions
- Key up events

---

#### AnyKeyPressHandler

**Purpose**: Triggers when any key is pressed.

**Requirement**: None (global handler)

**Properties**:
- `repeat`: bool - Include keyboard repeat events

**Callback Data**: `tuple` of `Key` enum values pressed this frame

**Example**:
```python
def log_key_press(sender, target, keys):
    for key in keys:
        print(f"Key pressed: {key}")

C.viewport.handlers += [
    dcg.AnyKeyPressHandler(C, callback=log_key_press)
]
```

**Use Cases**:
- Key logging
- Global key event monitoring
- Custom key mapping systems

---

#### AnyKeyReleaseHandler

**Purpose**: Triggers when any key is released.

**Requirement**: None (global handler)

**Properties**: None

**Callback Data**: `tuple` of `Key` enum values released this frame

**Example**:
```python
C.viewport.handlers += [
    dcg.AnyKeyReleaseHandler(C,
        callback=lambda s,t,keys: handle_key_up(keys))
]
```

**Use Cases**:
- Monitoring all key releases
- Input recording
- Chord detection

---

#### AnyKeyDownHandler

**Purpose**: Triggers while any key is held down.

**Requirement**: None (global handler)

**Properties**: None

**Callback Data**: `tuple` of `(Key, duration)` tuples for all keys currently down

**Example**:
```python
def monitor_keys(sender, target, key_durations):
    for key, duration in key_durations:
        if duration > 2.0:
            print(f"{key} held for {duration} seconds")

C.viewport.handlers += [
    dcg.AnyKeyDownHandler(C, callback=monitor_keys)
]
```

**Use Cases**:
- Multi-key detection
- Chord combinations
- Key hold tracking

---

### Global Mouse Handlers

Global mouse handlers monitor mouse state anywhere in the viewport. Like keyboard handlers, they can be attached to any item but only run when rendered. Usually attached to viewport.

#### MouseClickHandler

**Purpose**: Triggers when a mouse button is clicked anywhere.

**Requirement**: None (global handler)

**Properties**:
- `button`: `dcg.MouseButton` (LEFT, RIGHT, MIDDLE, X1, X2)
- `repeat`: bool - Keyboard repeat behavior for mouse (rare)

**Callback Data**: `button` (int)

**Example**:
```python
# Detect clicks anywhere
C.viewport.handlers += [
    dcg.MouseClickHandler(C, button=dcg.MouseButton.LEFT,
        callback=lambda s,t,btn: handle_global_click())
]

# Close menu on any click
C.viewport.handlers += [
    dcg.MouseClickHandler(C, button=dcg.MouseButton.LEFT,
        callback=lambda s,t,btn: close_context_menu())
]
```

**Use Cases**:
- Click-outside-to-close behavior
- Global click tracking
- Canvas click detection

---

#### MouseDoubleClickHandler

**Purpose**: Triggers on double-click anywhere.

**Requirement**: None (global handler)

**Properties**:
- `button`: `dcg.MouseButton`

**Callback Data**: `button` (int)

**Example**:
```python
C.viewport.handlers += [
    dcg.MouseDoubleClickHandler(C, button=dcg.MouseButton.LEFT,
        callback=lambda s,t,btn: handle_double_click())
]
```

**Use Cases**:
- Global double-click actions
- Canvas zoom-to-fit
- Quick actions

---

#### MouseDownHandler

**Purpose**: Triggers continuously while mouse button is held down anywhere.

**Requirement**: None (global handler)

**Properties**:
- `button`: `dcg.MouseButton`

**Callback Data**: `(button, duration)` tuple

**Example**:
```python
C.viewport.handlers += [
    dcg.MouseDownHandler(C, button=dcg.MouseButton.RIGHT,
        callback=lambda s,t,(btn,dur): show_context_menu_timer(dur))
]
```

**Use Cases**:
- Hold-to-action
- Custom drag detection
- Timed actions

---

#### MouseReleaseHandler

**Purpose**: Triggers when mouse button is released.

**Requirement**: None (global handler)

**Properties**:
- `button`: `dcg.MouseButton`

**Callback Data**: `button` (int)

**Example**:
```python
C.viewport.handlers += [
    dcg.MouseReleaseHandler(C, button=dcg.MouseButton.LEFT,
        callback=lambda s,t,btn: finalize_drag())
]
```

**Use Cases**:
- Drag completion
- Mouse up events
- Release actions

---

#### MouseDragHandler

**Purpose**: Triggers when mouse is dragging anywhere (button down + movement).

**Requirement**: None (global handler)

**Properties**:
- `button`: `dcg.MouseButton`
- `threshold`: float - Pixels of movement before drag starts (default: system setting)

**Callback Data**: `(delta_x, delta_y)` tuple - Movement since last frame

**Example**:
```python
# Canvas panning with middle mouse
C.viewport.handlers += [
    dcg.MouseDragHandler(C, button=dcg.MouseButton.MIDDLE,
        callback=lambda s,t,(dx,dy): pan_canvas(dx, dy))
]
```

**Use Cases**:
- Canvas panning
- Camera control
- Global drag operations

---

#### MouseMoveHandler

**Purpose**: Triggers when mouse moves anywhere.

**Requirement**: None (global handler)

**Properties**: None

**Callback Data**: `(x, y)` tuple - Current mouse position

**Example**:
```python
C.viewport.handlers += [
    dcg.MouseMoveHandler(C,
        callback=lambda s,t,(x,y): update_cursor_coords(x, y))
]
```

**Use Cases**:
- Cursor tracking
- Mouse trail effects
- Position-based logic

**Performance Warning**: Triggers on every mouse movement, keep callback lightweight.

---

#### MouseWheelHandler

**Purpose**: Triggers on mouse wheel scroll.

**Requirement**: None (global handler)

**Properties**:
- `horizontal`: bool - If True, monitors horizontal scroll (if available)

**Callback Data**: `float` - Scroll amount (positive = up/right, negative = down/left)

**Example**:
```python
# Zoom with mouse wheel
C.viewport.handlers += [
    dcg.MouseWheelHandler(C,
        callback=lambda s,t,delta: zoom_view(delta))
]

# Horizontal scroll
C.viewport.handlers += [
    dcg.MouseWheelHandler(C, horizontal=True,
        callback=lambda s,t,delta: scroll_horizontal(delta))
]
```

**Use Cases**:
- Zooming
- Scrolling
- Value adjustment

---

#### MouseInRect

**Purpose**: Triggers when mouse is within a specified rectangle.

**Requirement**: None (global handler)

**Properties**:
- `x1`, `y1`: Top-left corner (float)
- `x2`, `y2`: Bottom-right corner (float)

**Callback Data**: None

**Example**:
```python
# Detect mouse in specific screen region
C.viewport.handlers += [
    dcg.MouseInRect(C, x1=100, y1=100, x2=300, y2=300,
        callback=lambda s,t,d: highlight_region())
]
```

**Use Cases**:
- Region-based detection
- Custom hotspots
- Screen area monitoring

---

#### AnyMouseClickHandler / AnyMouseDoubleClickHandler / AnyMouseReleaseHandler / AnyMouseDownHandler

**Purpose**: Monitor all mouse buttons simultaneously.

**Requirement**: None (global handler)

**Properties**: None (monitors all buttons)

**Callback Data**:
- Click/Release handlers: `tuple` of buttons pressed/released
- Down handler: `tuple` of `(button, duration)` tuples

**Example**:
```python
C.viewport.handlers += [
    dcg.AnyMouseClickHandler(C,
        callback=lambda s,t,buttons: handle_any_click(buttons))
]
```

**Use Cases**:
- Multi-button detection
- Universal mouse handling
- Input recording

---

### Drag & Drop Handlers

Drag & drop handlers implement drag-and-drop functionality between items.

#### DragDropSourceHandler

**Purpose**: Makes an item a drag source - clicking and dragging creates a draggable payload.

**Requirement**: Special drag & drop capability (most items support this)

**Properties**:
- `flags`: int - ImGui drag & drop flags
- `overwrite`: bool - Overwrite existing drag source
- `drag_type`: str - Type identifier for drag payload

**Callback Data**: None

**Example**:
```python
# Make text draggable
draggable_text = dcg.Text(C, value="Drag me")
source_handler = dcg.DragDropSourceHandler(C, drag_type="TEXT_ITEM")
draggable_text.handlers += [source_handler]

# Add visual feedback
with dcg.Tooltip(C) as tooltip:
    dcg.Text(C, value="Dragging...")
source_handler.preview = tooltip
```

**Use Cases**:
- File browser drag operations
- Inventory systems in games
- Reorderable lists

**Note**: You need both a source and a target handler to complete drag & drop.

---

#### DragDropActiveHandler

**Purpose**: Monitors active drag & drop operations - triggers while dragging.

**Requirement**: None (global handler)

**Properties**:
- `any_target`: bool - Monitor any drag type
- `items`: list - Specific drag types to monitor

**Callback Data**: None

**Example**:
```python
# Visual feedback during drag
active_handler = dcg.DragDropActiveHandler(C, any_target=True,
    callback=lambda s,t,d: show_drop_indicator())
C.viewport.handlers += [active_handler]
```

**Use Cases**:
- Visual feedback during drag
- Global drag state
- Preventing other interactions while dragging

---

#### DragDropTargetHandler

**Purpose**: Makes an item a drop target - accepts specific drag payloads.

**Requirement**: None (can be attached to most items)

**Properties**:
- `flags`: int - ImGui drag & drop flags
- `items`: list - Drag types this target accepts

**Callback Data**: Dictionary with drop information (source item, payload, etc.)

**Example**:
```python
# Create drop target
drop_zone = dcg.Text(C, value="Drop here")
target_handler = dcg.DragDropTargetHandler(C,
    items=["TEXT_ITEM"],
    callback=lambda s,t,d: handle_drop(d))
drop_zone.handlers += [target_handler]

def handle_drop(data):
    source = data.get('source')
    payload = data.get('payload')
    print(f"Dropped {payload} from {source}")
```

**Use Cases**:
- Drop zones in UI
- Inventory slots
- File upload areas

---

## Component Compatibility

### Capability Reference

Handlers verify item capabilities before binding. Here's what capabilities enable which handlers:

| Capability | Description | Handler Types | Example Components |
|------------|-------------|---------------|-------------------|
| `can_be_active` | Item can be activated | Activated, Active, Deactivated | Button, Checkbox, RadioButton, Selectable |
| `can_be_clicked` | Item can be clicked | Clicked, DoubleClicked | Most visible items |
| `can_be_dragged` | Item can be dragged | Dragged, Dragging | Items with `button=True` |
| `can_be_edited` | Item value can be edited | Edited | InputText, Slider, DragFloat, ColorEdit |
| `can_be_deactivated_after_edited` | Detects edit completion | DeactivatedAfterEdit | InputText, InputInt, InputFloat |
| `can_be_focused` | Item can receive keyboard focus | Focus, GotFocus, LostFocus | Window, InputText, ChildWindow |
| `can_be_hovered` | Item can be hovered | Hover, GotHover, LostHover | Most visible items |
| `can_be_toggled` | Item can open/close | ToggledOpen, ToggledClose, Open, Close | TreeNode, CollapsingHeader |
| `has_position` | Item has position | Motion, MouseOver variants | All positioned items |
| `has_rect_size` | Item has size | Resize, MouseOver variants | All visible items |
| `has_content_region` | Item has content area | ContentResize | Window, ChildWindow, Group |

### Global Handlers

These handlers don't require specific item capabilities and can be attached to any item:
- All keyboard handlers (KeyDown, KeyPress, etc.)
- All global mouse handlers (MouseClick, MouseDrag, etc.)
- RenderHandler, GotRenderHandler, LostRenderHandler
- MouseCursorHandler (use with ConditionalHandler)
- DragDropActiveHandler

**Important**: Global handlers only execute when their attached item is rendered. To ensure global handlers always run, attach them to the viewport:

```python
C.viewport.handlers += [
    dcg.KeyPressHandler(C, key=dcg.Key.ESCAPE, callback=quit_app),
    dcg.MouseWheelHandler(C, callback=global_zoom)
]
```

---

## Usage Patterns

### Pattern 1: Simple Event Handling

Direct callback on single event:

```python
button = dcg.Button(C, label="Click me")
button.handlers += [
    dcg.ClickedHandler(C, callback=lambda s,t,d: print("Clicked!"))
]
```

---

### Pattern 2: Multiple Handlers on One Item

Respond to different events:

```python
button = dcg.Button(C, label="Interactive")
button.handlers += [
    dcg.ClickedHandler(C, callback=on_click),
    dcg.DoubleClickedHandler(C, callback=on_double_click),
    dcg.HoverHandler(C, callback=on_hover),
    dcg.GotFocusHandler(C, callback=on_focus)
]
```

---

### Pattern 3: Conditional Execution with ConditionalHandler

Execute action only when multiple conditions are met:

```python
# Change cursor only when hovering AND Shift key is down
button = dcg.Button(C, label="Conditional")
with dcg.ConditionalHandler(C) as conditional:
    # First child - the action
    dcg.MouseCursorHandler(C, cursor=dcg.MouseCursor.HAND)
    # Other children - conditions
    dcg.HoverHandler(C)
    dcg.KeyDownHandler(C, key=dcg.Key.SHIFT)
button.handlers += [conditional]
```

---

### Pattern 4: Logical Combinations with HandlerList

Combine multiple conditions with AND/OR/NONE logic:

```python
# Trigger when hovering AND Ctrl key is down
with dcg.HandlerList(C, op=dcg.HandlerListOP.ALL,
                     callback=special_action) as combo:
    dcg.HoverHandler(C)
    dcg.KeyDownHandler(C, key=dcg.Key.CTRL)
button.handlers += [combo]

# Trigger when EITHER hovering OR focused
with dcg.HandlerList(C, op=dcg.HandlerListOP.ANY,
                     callback=highlight) as combo:
    dcg.HoverHandler(C)
    dcg.FocusHandler(C)
button.handlers += [combo]
```

---

### Pattern 5: Temporary One-Time Handlers

Handler that removes itself after first trigger:

```python
from dearcygui.utils.handler import auto_cleanup_handler

handler = dcg.ClickedHandler(C, callback=first_time_setup)
auto_cleanup_handler(handler)  # Removes after first trigger
button.handlers += [handler]
```

---

### Pattern 6: Async Event Handling with Futures

Wait for events asynchronously:

```python
from dearcygui.utils.handler import future_from_handlers
import asyncio

async def wait_for_click():
    handler = dcg.ClickedHandler(C)
    button.handlers += [handler]

    future = future_from_handlers(handler, cleanup=True)
    sender, target, data = await asyncio.wrap_future(future)
    print("Button was clicked!")

# Run in async context
asyncio.run(wait_for_click())
```

---

### Pattern 7: Event Streams with Generators

Process continuous event stream:

```python
from dearcygui.utils.handler import generator_from_handlers
import time

handler = dcg.EditedHandler(C)
slider.handlers += [handler]

gen = generator_from_handlers(handler)
for sender, target, data in gen:
    print(f"Slider value: {target.value} at {time.time()}")
    if target.value > 90:
        break  # Stop listening
```

---

### Pattern 8: Cross-Item Dependencies with OtherItemHandler

Monitor one item while interacting with another:

```python
slider = dcg.SliderFloat(C, label="Volume", max_value=100)
button = dcg.Button(C, label="Auto-enable at 50+")

# Button handler monitors slider
other = dcg.OtherItemHandler(C, target=slider)
other.handlers += [
    dcg.EditedHandler(C, callback=lambda s,t,d:
        enable_feature() if slider.value > 50 else disable_feature())
]
button.handlers += [other]
```

---

### Pattern 9: Keyboard Shortcuts

Global keyboard shortcuts on viewport:

```python
C.viewport.handlers += [
    # Ctrl+S to save
    dcg.HandlerList(C, op=dcg.HandlerListOP.ALL, callback=save_file, children=[
        dcg.KeyDownHandler(C, key=dcg.Key.CTRL),
        dcg.KeyPressHandler(C, key=dcg.Key.S)
    ]),
    # Escape to quit
    dcg.KeyPressHandler(C, key=dcg.Key.ESCAPE, callback=quit_app),
    # F11 to toggle fullscreen
    dcg.KeyPressHandler(C, key=dcg.Key.F11, callback=toggle_fullscreen)
]
```

---

### Pattern 10: Tooltip with Hover

Show/hide tooltip on hover:

```python
button = dcg.Button(C, label="Info")

# Create tooltip
tooltip = dcg.Tooltip(C)
dcg.Text(C, value="This is helpful information", parent=tooltip)
tooltip.show = False

# Show on hover, hide on leave
button.handlers += [
    dcg.GotHoverHandler(C, callback=lambda s,t,d: setattr(tooltip, 'show', True)),
    dcg.LostHoverHandler(C, callback=lambda s,t,d: setattr(tooltip, 'show', False))
]
```

---

### Pattern 11: Custom Handler for Complex Logic

Create reusable custom handler:

```python
class ValueThresholdHandler(dcg.CustomHandler):
    def __init__(self, context, threshold=50, **kwargs):
        super().__init__(context, **kwargs)
        self.threshold = threshold

    def check_can_bind(self, item):
        # Only bind to items with 'value' attribute
        return hasattr(item, 'value')

    def check_status(self, item):
        # Trigger when value exceeds threshold
        return item.value > self.threshold

slider = dcg.SliderFloat(C, max_value=100)
slider.handlers += [
    ValueThresholdHandler(C, threshold=75,
        callback=lambda s,t,d: print("Warning: High value!"))
]
```

---

### Pattern 12: Drag and Drop

Complete drag & drop implementation:

```python
# Source item
source = dcg.Text(C, value="Drag me")
source_handler = dcg.DragDropSourceHandler(C, drag_type="ITEM")
source.handlers += [source_handler]

# Visual preview during drag
with dcg.Tooltip(C) as preview:
    dcg.Text(C, value="Dragging item...")
source_handler.preview = preview

# Target item
target = dcg.Text(C, value="Drop here")
target.handlers += [
    dcg.DragDropTargetHandler(C, items=["ITEM"],
        callback=lambda s,t,d: handle_drop(d))
]

def handle_drop(data):
    source_item = data['source']
    print(f"Dropped {source_item.value}")
```

---

### Pattern 13: Disable/Enable Handler Groups

Control handler execution with BoolHandler:

```python
enabled = dcg.SharedBool(C, value=True)

# All interactions controlled by enabled flag
button = dcg.Button(C, label="Conditional Interactions")
for handler_callback in [action1, action2, action3]:
    with dcg.HandlerList(C, op=dcg.HandlerListOP.ALL,
                         callback=handler_callback) as combo:
        dcg.ClickedHandler(C)
        dcg.BoolHandler(C, condition=enabled)
    button.handlers += [combo]

# Toggle from elsewhere
enabled.value = False  # Disable all interactions
```

---

### Pattern 14: Canvas Interaction

Implement canvas with pan and zoom:

```python
canvas = dcg.DrawInWindow(C, width=800, height=600)

# Pan with middle mouse
C.viewport.handlers += [
    dcg.MouseDragHandler(C, button=dcg.MouseButton.MIDDLE,
        callback=lambda s,t,(dx,dy): pan_canvas(dx, dy))
]

# Zoom with mouse wheel
C.viewport.handlers += [
    dcg.MouseWheelHandler(C, callback=lambda s,t,delta: zoom_canvas(delta))
]

# Click on canvas
canvas.handlers += [
    dcg.ClickedHandler(C, callback=lambda s,t,d: add_point_at_mouse())
]
```

---

### Pattern 15: Form Validation

Validate input fields:

```python
email_input = dcg.InputText(C, label="Email")
password_input = dcg.InputText(C, label="Password", password=True)
submit_btn = dcg.Button(C, label="Submit")

# Real-time validation
email_input.handlers += [
    dcg.EditedHandler(C, callback=lambda s,t,d: validate_email_format(t.value))
]

# Validation on focus loss
email_input.handlers += [
    dcg.LostFocusHandler(C, callback=lambda s,t,d:
        show_error() if not is_valid_email(t.value) else clear_error())
]

# Submit validation
submit_btn.handlers += [
    dcg.ClickedHandler(C, callback=lambda s,t,d:
        submit_form() if validate_all() else show_validation_errors())
]
```

---

## Advanced Topics

### Thread Safety

All handler operations are mutex-protected and thread-safe:

```python
import threading

def background_thread():
    # Safe to modify handlers from another thread
    button.handlers += [dcg.ClickedHandler(C, callback=new_action)]

threading.Thread(target=background_thread).start()
```

**Note**: Handler callbacks execute in the context's rendering thread, not the thread that attached them.

---

### Performance Considerations

1. **RenderHandler**: Called every frame - keep callbacks extremely lightweight
2. **CustomHandler**: Executes Python code every frame - use sparingly
3. **MouseMoveHandler**: Triggers on every pixel of movement - optimize carefully
4. **EditedHandler**: Triggers continuously during editing - consider DeactivatedAfterEditHandler for non-realtime updates

**Optimization Strategy**:
```python
# Bad - Heavy computation every frame
item.handlers += [
    dcg.RenderHandler(C, callback=lambda s,t,d: expensive_computation())
]

# Good - Only compute when state changes
item.handlers += [
    dcg.EditedHandler(C, callback=lambda s,t,d: expensive_computation())
]

# Better - Defer computation to after editing
item.handlers += [
    dcg.DeactivatedAfterEditHandler(C,
        callback=lambda s,t,d: expensive_computation())
]
```

---

### Handler Execution Order

Handlers execute in the order they're added:

```python
button.handlers += [
    dcg.ClickedHandler(C, callback=lambda s,t,d: print("First")),
    dcg.ClickedHandler(C, callback=lambda s,t,d: print("Second")),
    dcg.ClickedHandler(C, callback=lambda s,t,d: print("Third"))
]
# Output on click: First, Second, Third
```

**Note**: All callbacks for a frame are queued and executed after rendering completes.

---

### Conditional Handler Logic

Use `ConditionalHandler` to skip expensive operations:

```python
# Without ConditionalHandler - cursor change runs every frame
with dcg.HandlerList(C, op=dcg.HandlerListOP.ALL) as combo:
    dcg.MouseCursorHandler(C, cursor=dcg.MouseCursor.HAND)
    dcg.HoverHandler(C)
    dcg.KeyDownHandler(C, key=dcg.Key.SHIFT)
button.handlers += [combo]

# With ConditionalHandler - only checks cursor when conditions met
with dcg.ConditionalHandler(C) as conditional:
    dcg.MouseCursorHandler(C, cursor=dcg.MouseCursor.HAND)  # First child
    dcg.HoverHandler(C)  # Condition
    dcg.KeyDownHandler(C, key=dcg.Key.SHIFT)  # Condition
button.handlers += [conditional]
```

---

### Handler Lifecycle Management

```python
# Create handlers
handler1 = dcg.ClickedHandler(C, callback=action1)
handler2 = dcg.HoverHandler(C, callback=action2)

# Attach
button.handlers += [handler1, handler2]

# Disable without removing
handler1.enabled = False  # Stop processing

# Re-enable
handler1.enabled = True

# Remove specific handler
button.handlers = [h for h in button.handlers if h != handler1]

# Clear all handlers
button.handlers = []

# Handlers are automatically cleaned up when item is destroyed
button.destroy()  # Handlers are freed
```

---

### Global vs Item-Specific Handlers

**Global handlers** (keyboard, mouse) can attach to any item but only run when rendered:

```python
# Attached to viewport - always runs
C.viewport.handlers += [
    dcg.KeyPressHandler(C, key=dcg.Key.SPACE, callback=global_action)
]

# Attached to window - only runs when window is rendered
window = dcg.Window(C, label="Settings")
window.handlers += [
    dcg.KeyPressHandler(C, key=dcg.Key.SPACE, callback=window_action)
]
window.show = False  # Handler won't run

# Best practice: Attach global handlers to viewport
```

---

### Debugging Handlers

```python
def debug_callback(sender, target, data):
    print(f"Handler: {sender.__class__.__name__}")
    print(f"Target: {target}")
    print(f"Data: {data}")
    print(f"Handler enabled: {sender.enabled}")

button = dcg.Button(C, label="Debug")
button.handlers += [
    dcg.ClickedHandler(C, callback=debug_callback)
]
```

---

### Memory Management

Handlers hold references to callbacks and items:

```python
# Circular reference - handler holds callback which references item
def make_button():
    button = dcg.Button(C, label="Click")
    button.handlers += [
        dcg.ClickedHandler(C, callback=lambda s,t,d: button.label = "Clicked")
    ]
    return button

# To avoid leaks, clear handlers when done
button = make_button()
# Later...
button.handlers = []  # Clear before destroying
button.destroy()
```

**Best Practice**: Use weak references or avoid capturing item in callback:

```python
# Good - use target parameter
button.handlers += [
    dcg.ClickedHandler(C, callback=lambda s,t,d: setattr(t, 'label', "Clicked"))
]
```

---

## Common Use Cases

### Use Case 1: Interactive Tooltip

Show detailed information on hover:

```python
button = dcg.Button(C, label="Hover for info")

# Create tooltip window
tooltip = dcg.Tooltip(C)
with tooltip:
    dcg.Text(C, value="Detailed Information:")
    dcg.Separator(C)
    dcg.Text(C, value="This button performs an action")
tooltip.show = False

# Show/hide on hover
button.handlers += [
    dcg.GotHoverHandler(C, callback=lambda s,t,d: setattr(tooltip, 'show', True)),
    dcg.LostHoverHandler(C, callback=lambda s,t,d: setattr(tooltip, 'show', False))
]
```

---

### Use Case 2: Animated Progress Bar

Update progress bar every frame:

```python
progress = dcg.ProgressBar(C, value=0.0)
start_time = time.time()

def update_progress(sender, target, data):
    elapsed = time.time() - start_time
    target.value = min(elapsed / 10.0, 1.0)  # 10 second duration
    if target.value >= 1.0:
        sender.enabled = False  # Stop when complete

progress.handlers += [
    dcg.RenderHandler(C, callback=update_progress)
]
```

---

### Use Case 3: Auto-Save on Edit

Save data after user stops editing:

```python
text_editor = dcg.InputTextMultiline(C, width=400, height=300)

def auto_save(sender, target, data):
    save_to_file(target.value)
    print("Auto-saved!")

text_editor.handlers += [
    dcg.DeactivatedAfterEditHandler(C, callback=auto_save)
]
```

---

### Use Case 4: Context Menu

Show context menu on right-click:

```python
item = dcg.Text(C, value="Right-click me")
context_menu = dcg.Window(C, label="Context Menu", modal=True)
context_menu.show = False

with context_menu:
    dcg.Button(C, label="Copy", callback=lambda s,t,d: copy_item())
    dcg.Button(C, label="Delete", callback=lambda s,t,d: delete_item())

item.handlers += [
    dcg.ClickedHandler(C, button=dcg.MouseButton.RIGHT,
        callback=lambda s,t,d: setattr(context_menu, 'show', True))
]
```

---

### Use Case 5: Keyboard Navigation

Navigate list with arrow keys:

```python
items = [dcg.Selectable(C, label=f"Item {i}") for i in range(10)]
current_index = [0]  # Mutable for closure

def select_previous(s, t, k):
    current_index[0] = max(0, current_index[0] - 1)
    items[current_index[0]].value = True

def select_next(s, t, k):
    current_index[0] = min(len(items) - 1, current_index[0] + 1)
    items[current_index[0]].value = True

C.viewport.handlers += [
    dcg.KeyPressHandler(C, key=dcg.Key.UP_ARROW, callback=select_previous),
    dcg.KeyPressHandler(C, key=dcg.Key.DOWN_ARROW, callback=select_next)
]
```

---

### Use Case 6: Drag to Reorder List

Implement reorderable list items:

```python
items = ["Item 1", "Item 2", "Item 3"]

for i, item_text in enumerate(items):
    text = dcg.Text(C, value=item_text, tag=f"item_{i}")

    # Make draggable
    source = dcg.DragDropSourceHandler(C, drag_type="LIST_ITEM")
    source.payload = i  # Store index
    text.handlers += [source]

    # Make drop target
    def handle_drop(sender, target, data):
        source_idx = data['payload']
        target_idx = int(target.tag.split('_')[1])
        items[source_idx], items[target_idx] = items[target_idx], items[source_idx]
        rebuild_list()

    target = dcg.DragDropTargetHandler(C, items=["LIST_ITEM"], callback=handle_drop)
    text.handlers += [target]
```

---

### Use Case 7: Lazy-Loading Tree

Load tree node children only when expanded:

```python
def create_tree_node(label, has_children=True):
    node = dcg.TreeNode(C, label=label)

    if has_children:
        # Placeholder
        dcg.Text(C, value="Loading...", parent=node)

        def load_children(sender, target, data):
            # Remove placeholder
            for child in target.children:
                child.destroy()

            # Load actual children
            for i in range(5):
                dcg.Text(C, value=f"Child {i}", parent=target)

            # Remove handler after first load
            sender.enabled = False

        node.handlers += [
            dcg.ToggledOpenHandler(C, callback=load_children)
        ]

    return node

root = create_tree_node("Root Folder")
```

---

### Use Case 8: Click-Outside-to-Close

Close popup when clicking outside:

```python
popup = dcg.Window(C, label="Popup", modal=False)
popup.show = True

def check_click_outside(sender, target, button):
    mouse_x, mouse_y = C.viewport.mouse_pos
    if not popup.is_mouse_hovering():
        popup.show = False
        sender.enabled = False  # Stop checking

C.viewport.handlers += [
    dcg.MouseClickHandler(C, button=dcg.MouseButton.LEFT,
        callback=check_click_outside)
]
```

---

### Use Case 9: Real-time Character Counter

Count characters as user types:

```python
text_input = dcg.InputTextMultiline(C, width=400, height=200)
counter = dcg.Text(C, value="Characters: 0")

def update_counter(sender, target, data):
    char_count = len(target.value)
    counter.value = f"Characters: {char_count}"

text_input.handlers += [
    dcg.EditedHandler(C, callback=update_counter)
]
```

---

### Use Case 10: Game-style Controls

WASD movement with space to jump:

```python
player_pos = [0, 0]
velocity = [0, 0]

def move_left(s, t, (k, dur)):
    velocity[0] = -5

def move_right(s, t, (k, dur)):
    velocity[0] = 5

def jump(s, t, k):
    velocity[1] = 10

C.viewport.handlers += [
    dcg.KeyDownHandler(C, key=dcg.Key.A, callback=move_left),
    dcg.KeyDownHandler(C, key=dcg.Key.D, callback=move_right),
    dcg.KeyPressHandler(C, key=dcg.Key.SPACE, callback=jump),
    dcg.KeyReleaseHandler(C, key=dcg.Key.A, callback=lambda s,t,k: velocity.__setitem__(0, 0)),
    dcg.KeyReleaseHandler(C, key=dcg.Key.D, callback=lambda s,t,k: velocity.__setitem__(0, 0))
]
```

---

## Summary

DearCyGui's handler system provides a powerful, declarative approach to building interactive UIs:

- **50+ handler types** covering all interaction patterns
- **Composable** with HandlerList and ConditionalHandler
- **Performant** with capability-based binding and conditional execution
- **Flexible** supporting global and item-specific handlers
- **Thread-safe** for multi-threaded applications

### Quick Reference: Most Common Handlers

1. **ClickedHandler** - Button clicks and interactions
2. **HoverHandler / GotHoverHandler / LostHoverHandler** - Mouse hover detection
3. **EditedHandler / DeactivatedAfterEditHandler** - Input field changes
4. **KeyPressHandler** - Keyboard shortcuts
5. **RenderHandler** - Per-frame updates and animations
6. **ToggledOpenHandler / ToggledCloseHandler** - Tree node expansion
7. **MouseDragHandler** - Canvas panning and dragging
8. **MouseWheelHandler** - Zooming and scrolling

### File Reference

- **Handler implementations**: `/dearcygui/handler.pyx`
- **Handler declarations**: `/dearcygui/handler.pxd`
- **Handler utilities**: `/dearcygui/utils/handler.py`
- **Advanced documentation**: `/dearcygui/docs/advanced.md`

---

*This documentation covers DearCyGui handlers comprehensively. For more examples, see the test files and example applications in the repository.*
