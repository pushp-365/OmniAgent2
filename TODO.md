# TODO - Chat Issues Fix

## Issues to Fix:
1. [ ] Fix ChatLogIntegration in Main.py - Load only the current chat's messages instead of ALL chats
2. [ ] Add role prefix to messages in Main.py - Store messages as "USER: ..." and "ASSISTANT: ..." in Responses.data
3. [ ] Update GUI to parse roles in GUI_1.PY - Parse the role prefix and apply different colors

## Implementation Steps:

### Step 1: Fix ChatLogIntegration in Main.py
- [ ] Modify ChatLogIntegration() to load only messages from current_chat_id
- [ ] Read current chat ID from CurrentChat.data file

### Step 2: Add role prefix to messages in Main.py
- [ ] Modify ShowTextToScreen to include role prefix (USER: or ASSISTANT:)
- [ ] Update both user and assistant message displays

### Step 3: Update GUI to parse roles in GUI_1.PY
- [ ] Modify loadMessages to parse role prefix
- [ ] Update addMessage to accept role parameter
- [ ] Apply different colors for user (green) vs assistant (blue/white)

## Files to Edit:
- Main.py
- Frontend/GUI_1.PY
