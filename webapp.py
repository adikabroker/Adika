Act as an elite Senior Full-Stack Software Engineer and Expert UI/UX Designer.

I need you to refactor and upgrade the `webapp.py` code for the "Adika Marketplace" Telegram Mini App. Maintain all Flask API endpoints, database interactions, and backend logic, but strictly apply the following UI/UX fixes:

### 🎯 REQUIRED UI/UX CORRECTIONS:

1. Color Palette (Header & Body Background):
   - Header Background Color: Set strictly to Teal Teal/Cyan `#16acbd` (`bg-[#16acbd] text-white`).
   - Main Body Background Color: Set strictly to Light Cyan/Ice Blue `#b5eff3` (`bg-[#b5eff3] min-h-screen`).

2. Floating Cards with Thin Frame & Dark Elevated Shadow:
   - Match Telegram-style card aesthetics:
     * Extremely thin clean border (`border border-slate-200/80` or `border-white/60`).
     * Solid crisp white background (`bg-white rounded-2xl`).
     * Floating 3D dark shadow that makes cards look elevated off the `#b5eff3` background (`shadow-[0_12px_28px_rgba(15,23,42,0.12)]`).

3. Fixed Sticky Header (Integrated Search & Tabs):
   - Lock Header at the top using `fixed top-0 left-0 right-0 z-50 bg-[#16acbd] shadow-md p-3`.
   - Ensure the main content container has adequate top padding (`pt-36` or similar) so cards NEVER get hidden behind the header during scrolling.
   - Segmented Tabs (Marketplace / Buyers) & Search bar styled cleanly against the `#16acbd` header background.

4. Telegram-Native Floating Bottom Nav & Dynamic "+" Button:
   - Translucent floating bottom bar (`fixed bottom-4 left-4 right-4 bg-white/95 backdrop-blur-xl rounded-full shadow-2xl border border-white/60 p-2 z-40 flex items-center justify-around`).
   - Active tab indicator pill with matching teal theme (`bg-[#16acbd]/15 text-[#16acbd] rounded-full px-4 py-1.5 flex flex-col items-center transition-all`).
   - Clean SVG icons with English labels ("Home", "Search", "Messages", "Help").
   - Dynamic "+" Floating Action Button in the center:
     * Marketplace Tab -> Opens "Submit Listing" form.
     * Buyers Tab -> Opens "Submit Request" form.

5. Fix Bottom-Sheet Detail Modal Action Buttons Overflow:
   - Ensure "Call" (ደውል) and "Telegram" (ቴሌግራም) action buttons are never cut off at the bottom.
   - Structure Modal as a flex column (`max-h-[85vh] flex flex-col bg-white rounded-t-3xl`):
     * Header & Close: Fixed top bar.
     * Content: Scrollable (`overflow-y-auto flex-1 p-4`).
     * Action Buttons: Fixed bottom footer (`p-3 bg-white border-t border-slate-100 shrink-0`).

### ⚠️ STRICT EXECUTION RULES:
- Return the 100% COMPLETE, RUNNABLE `webapp.py` code from line 1 to the end.
- DO NOT truncate, omit, or abbreviate any code block. Do not use placeholders like `# ... rest of the code ...`.
