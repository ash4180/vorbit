# Framework-Specific Patterns

## React

### Detection
```json
{
  "dependencies": {
    "react": "^18.x"
  }
}
```

### Component Pattern
```jsx
// Match existing component structure
// Usually: src/components/Feature/Feature.jsx

import { useState } from 'react';
import { Button } from '../ui/Button'; // Use existing UI

const MOCK_DATA = { /* ... */ };

export function FeaturePrototype() {
  const [data, setData] = useState(MOCK_DATA);

  return (
    <div className="..."> {/* Match existing class naming */}
      {/* Component content */}
    </div>
  );
}
```

### Common Locations
- Components: `src/components/`
- Pages: `src/pages/` or `app/`
- Styles: Check for CSS modules, Tailwind, styled-components

---

## Vue

### Detection
```json
{
  "dependencies": {
    "vue": "^3.x"
  }
}
```

### Component Pattern
```vue
<script setup>
import { ref } from 'vue'
import BaseButton from '@/components/ui/BaseButton.vue'

const MOCK_DATA = { /* ... */ }
const data = ref(MOCK_DATA)
</script>

<template>
  <div class="...">
    <!-- Component content -->
  </div>
</template>
```

### Common Locations
- Components: `src/components/`
- Pages: `src/views/` or `src/pages/`

---

## Svelte

### Detection
```json
{
  "devDependencies": {
    "svelte": "^4.x"
  }
}
```

### Component Pattern
```svelte
<script>
  import Button from '$lib/components/Button.svelte';

  const MOCK_DATA = { /* ... */ };
  let data = MOCK_DATA;
</script>

<div class="...">
  <!-- Component content -->
</div>
```

### Common Locations
- Components: `src/lib/components/`
- Routes: `src/routes/`

---

## Next.js

### Detection
```json
{
  "dependencies": {
    "next": "^14.x"
  }
}
```

### Component Pattern
```jsx
// App Router: app/prototype/page.jsx
// Pages Router: pages/prototype.jsx

'use client'; // For App Router with interactivity

import { useState } from 'react';

const MOCK_DATA = { /* ... */ };

export default function PrototypePage() {
  const [data, setData] = useState(MOCK_DATA);

  return (
    <main>
      {/* Page content */}
    </main>
  );
}
```

---

## Vanilla HTML/CSS

### Detection
No framework in package.json, or no package.json.

### Structure
```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Prototype: Feature Name</title>
  <link rel="stylesheet" href="prototype.css">
</head>
<body>
  <main id="app">
    <!-- Prototype content -->
  </main>

  <script>
    const MOCK_DATA = { /* ... */ };

    // Simple interactivity
    document.querySelector('...').addEventListener('click', () => {
      // Handle interaction
    });
  </script>
</body>
</html>
```

---

## Styling Detection

| Pattern | Look For |
|---------|----------|
| Tailwind | `tailwind.config.js`, classes like `flex p-4` |
| CSS Modules | `*.module.css` files |
| Styled Components | `styled-components` in deps |
| SCSS | `.scss` files |
| Plain CSS | `.css` files |

Always match the existing approach.
