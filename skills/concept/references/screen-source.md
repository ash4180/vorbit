# Screen Source

A drawing of an existing screen must match the real product: its layout, its components, its colors, its type and its features. A designer presents these drawings. A drawing that looks like a different product is useless.

The screen source file is the proof that you read the real code. The check compares every drawing with it.

## When you need one

- The screen, or a part of it, exists in the code: write a screen source file first, then draw.
- Nothing exists yet (a fresh idea for a new product): write `data-cf-source="none"` on the root. Never use `none` to skip reading code that exists.

## Step 1: Read the real screen

1. Find the page file of the screen, from the route or the navigation.
2. Open every component the page uses. Note the file of each one.
3. Find where the colors, fonts, radius and spacing come from: the theme file, the CSS variables, or the config of the styling tool.
4. List what the user can see and do on the screen: every navigation item, button, tab, filter, column and empty state.
5. Run the app and look at the screen when you can. Code alone does not show the final layout.

## Step 2: Write the file

Save it next to the frame files as `screen-source.json`. One file per screen.

```json
{
  "screen": { "name": "Tasks", "route": "/tasks", "file": "src/pages/Tasks/index.tsx" },
  "components": [
    { "name": "Button", "file": "src/components/ui/button.tsx" },
    { "name": "TaskRow", "file": "src/pages/Tasks/TaskRow.tsx" }
  ],
  "files": ["src/index.css", "tailwind.config.ts"],
  "colors": [
    { "value": "#0e0f12", "evidence": "--background: #0e0f12" },
    { "value": "#3ecf8e", "evidence": "bg-emerald-400" }
  ],
  "fonts": [{ "value": "Inter", "evidence": "Inter" }],
  "features": [
    { "label": "New task", "evidence": "New task" },
    { "label": "Projects", "evidence": "nav.projects" }
  ]
}
```

- Every `file` is a path from the root of the project, and must exist.
- `files` lists the other files your evidence comes from: theme, styles, config, text files.
- `evidence` is a piece of text copied from one of the listed files. It proves the entry is real: the hex, the variable name, the class name, the label, or the text key. Never write evidence from memory.
- `colors` holds every color the drawing uses, as hex, rgb or hsl.
- `features` holds every visible thing the user can do or go to. Leave nothing out because it is not part of your idea.
- Add `"repo": "<path>"` only when the frame files are saved outside the project.

## Step 3: Draw from it

- Use only the colors and fonts in the file. For a new color, an idea must say so in its subtitle, and the color goes in the file with evidence from the theme.
- Put `data-src="<component file>"` on each drawn part that is a real component. The attribute is invisible.
- Keep the real layout: the same regions, the same order, the same sizes and spacing.
- When the project has its design system as a canvas design system, install it on the canvas and mount its real components, as the canvas instructions say. A real component always beats a drawn copy.
- A `today` frame shows every feature in the file. An idea frame starts as a copy of the `today` drawing. Change only what the idea changes.

## What the check refuses

- A file in the list that does not exist.
- Evidence that is not found in the listed files.
- A color or a font in the drawing that is not in the file.
- A `data-src` that names a file outside `components`, or a drawing with no `data-src` at all.
- A `today` frame that leaves out a feature.

The check cannot measure layout. Keeping the real regions, order and spacing is yours to do.
