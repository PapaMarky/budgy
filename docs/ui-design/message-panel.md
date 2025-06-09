# Message Panel Design

## Overview

The MessagePanel provides user feedback through status messages, progress indication, and error reporting. It serves as the primary communication channel between the application and the user, displaying real-time information about ongoing operations and system status.

**Parent Container:** [Main Window (BudgyViewerApp)](main-window.md)

## Design Specifications

### Panel Properties

**Height:** `3 * BUTTON_HEIGHT + 4 * MARGIN`

**Width:** Full window width (1280px)

**Position:** Bottom of main window, anchored to bottom edge

**Container:** Direct child of BudgyViewerApp

### Layout Structure

The MessagePanel uses a three-row vertical layout with optional visibility:

```
┌─────────────────────────────────────────────────────────────┐
│ Row 1: [████████████████████████████████] (Progress Bar)   │
│        Centered, 90% of panel width, hidden by default     │
├─────────────────────────────────────────────────────────────┤
│ Row 2: [Info Message Text]                                 │
│        Left-aligned, full width, hidden by default         │
├─────────────────────────────────────────────────────────────┤
│ Row 3: [Error Message Text]                                │
│        Left-aligned, full width, hidden by default         │
└─────────────────────────────────────────────────────────────┘
```

## Functional Components

### 1. Progress Bar

**Purpose:** Visual indication of operation progress

**Properties:**
- Width: 90% of panel width
- Position: Centered horizontally
- Default State: Hidden (`visible=False`)
- Anchoring: Responsive to panel width changes

**Behavior:**
- Shows during long-running operations
- Updates progress percentage dynamically
- Automatically hidden when operation completes
- Provides visual feedback for user patience

### 2. Info Message Display

**Purpose:** General status and informational messages

**Properties:**
- Object ID: `#message-info` with `@bold-16` styling
- Position: Full width with margin
- Default State: Hidden (`visible=False`)
- Text: "Message Element" (placeholder)

**Message Types:**
- Operation confirmations
- Status updates during processing
- General user information
- Success notifications

### 3. Error Message Display

**Purpose:** Error notifications and warning messages

**Properties:**
- Object ID: `#message-error` with `@bold-16` styling
- Position: Full width with margin
- Default State: Hidden (`visible=False`)
- Color: Error-specific styling (red/warning colors)

**Message Types:**
- Database connection errors
- File operation failures
- Data validation warnings
- System error notifications

## Component Relationships

### Parent-Child Hierarchy
```
MessagePanel (UIPanel)
├── Progress Bar (UIProgressBar)
├── Info Message (UILabel)
└── Error Message (UILabel)
```

### Event System Integration
- **SHOW_MESSAGE Event:** Displays messages based on level
- **CLEAR_MESSAGES Event:** Hides all message displays
- Level mapping: `{'info': self.info, 'error': self.error}`

## State Management

### Visibility States

**Idle State:**
- All components hidden
- Panel appears empty
- Ready to receive new messages

**Progress State:**
- Progress bar visible and updating
- Message components may be visible
- Indicates ongoing operation

**Message State:**
- Info or error message visible
- Progress bar hidden (typically)
- User reading message content

**Combined State:**
- Progress bar and message both visible
- Used during complex operations
- Provides both progress and status information

### Message Level Handling

**Info Level Messages:**
- Uses `info()` method
- Shows in info message component
- Styled with standard info appearance
- Used for general status updates

**Error Level Messages:**
- Uses `error()` method  
- Shows in error message component
- Styled with error/warning appearance
- Used for problems and failures

## Event Handling

### Custom Events

**[SHOW_MESSAGE Event](https://github.com/PapaMarky/budgy/blob/main/src/budgy/gui/events.py):**
- **Purpose:** Display message with specified level
- **Parameters:** Message text, level ('info' or 'error')
- **Processing:** Routes to appropriate display method
- **Source:** Posted by various application components

**[CLEAR_MESSAGES Event](https://github.com/PapaMarky/budgy/blob/main/src/budgy/gui/events.py):**
- **Purpose:** Hide all message displays
- **Parameters:** None
- **Processing:** Sets all components to invisible
- **Source:** Posted after operations complete

### Event Processing Methods

```python
def handle_event(self, event):
    if event.type == SHOW_MESSAGE:
        level = event.level
        message = event.message
        if level in self.level_map:
            self.level_map[level](message)
    elif event.type == CLEAR_MESSAGES:
        self.clear_all_messages()
```

## Message Display Methods

### Info Message Display

**Method:** `info(message)`

**Behavior:**
- Sets info message text
- Makes info component visible
- Hides error component (mutual exclusion)
- Applies info-level styling

### Error Message Display

**Method:** `error(message)`

**Behavior:**
- Sets error message text
- Makes error component visible  
- Hides info component (mutual exclusion)
- Applies error-level styling

### Clear All Messages

**Method:** `clear_all_messages()`

**Behavior:**
- Hides progress bar
- Hides info message component
- Hides error message component
- Returns panel to idle state

## Progress Bar Management

### Progress Updates

**Method:** `update_progress(percentage)`

**Parameters:**
- `percentage`: Float between 0.0 and 1.0
- Represents completion percentage

**Behavior:**
- Makes progress bar visible if hidden
- Updates progress bar value
- Maintains visibility until explicitly cleared

### Progress Completion

**Automatic Handling:**
- Progress bar hidden when `clear_all_messages()` called
- Typically triggered after operation completion
- Can be manually controlled for complex workflows

## Styling and Theming

### Component Styling IDs

**Panel Container:**
- `#message-panel`: Overall panel styling

**Message Components:**
- `#message-info`: Info message styling with `@bold-16`
- `#message-error`: Error message styling with `@bold-16`

**Interactive Elements:**
- Progress bar uses default [pygame_gui](https://github.com/MyreMylar/pygame_gui) styling
- Responsive to theme color schemes

### Visual Hierarchy
- Bold 16pt font for all text messages
- Color coding for different message levels
- Consistent spacing and alignment
- Clear visual separation from other panels

## Layout and Positioning

### Responsive Design
- Progress bar scales with panel width (90%)
- Message text flows with available space
- Margins consistent with application standards
- Anchoring maintains position during resize

### Anchoring Strategy
```python
anchors={
    'top': 'bottom', 'left': 'left',
    'bottom': 'bottom', 'right': 'right'
}
```
- Anchored to bottom edge of window
- Maintains position relative to window bottom
- Adapts to window size changes

## Performance Considerations

### Efficient Updates
- Components created once and reused
- Visibility changes instead of recreation
- Minimal text processing overhead
- Event-driven updates only

### Memory Management
- Static component creation
- Event system integration
- No persistent message storage
- Garbage collection friendly

## Error Handling

### Graceful Degradation
- Handles missing message levels gracefully
- Falls back to default styling if theme missing
- Continues operation if individual components fail

### Event Processing Errors
- Invalid event types ignored safely
- Malformed message events handled gracefully
- System continues operation despite message failures

## Integration Points

### Application Integration
- Receives messages from all application components
- Provides unified feedback interface
- Integrates with operation lifecycle management

### Event System Integration
- Uses global event posting functions
- Consistent with application event patterns
- Supports asynchronous message delivery

### Database Operation Integration
- Shows progress during data imports
- Reports database operation status
- Handles database error reporting

## Usage Examples

### Showing Messages
```python
# Post info message (from anywhere in application)
from budgy.gui.events import post_show_message
post_show_message("Loading OFX data from file.ofx")

# Post error message
post_show_message("Database connection failed", level='error')

# Clear all messages
from budgy.gui.events import post_clear_messages
post_clear_messages()
```

**Source:** [`src/budgy/gui/message_panel.py`](https://github.com/PapaMarky/budgy/blob/main/src/budgy/gui/message_panel.py)

### Progress Bar Usage
```python
# During long operation
message_panel.update_progress(0.0)    # Start
message_panel.update_progress(0.5)    # Halfway
message_panel.update_progress(1.0)    # Complete
message_panel.clear_all_messages()    # Hide
```

## Accessibility Features

### Clear Communication
- High contrast text for readability
- Distinct styling for different message types
- Consistent positioning for user familiarity
- Bold text for importance emphasis

### User Experience
- Non-intrusive feedback placement
- Clear visual hierarchy
- Appropriate timing for message display
- Consistent behavior across operations

## Future Enhancements

### Potential Improvements
- Message history/logging capability
- Fade-in/fade-out animations
- Multiple message queuing
- Toast-style temporary messages

### Enhanced Progress Features
- Detailed progress text
- Cancellation capability for long operations
- Multi-stage progress indication
- Time remaining estimates

## Related Documentation
- [Main Window Design](main-window.md)
- [Event System Documentation](../Design_Notes.md#event-system)
- [MessagePanel Implementation](../ui-implementation/MessagePanel.md)