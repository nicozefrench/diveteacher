# Tailwind CSS + shadcn/ui Development Guide for AI Agent

> **Target**: Claude Sonnet 4.5 AI Agent for UX/UI Development  
> **Stack**: Tailwind CSS v3.4.0, Custom CSS Theme, shadcn/ui, clsx + tailwind-merge  
> **Last Updated**: October 2025

---

## Table of Contents

1. [Tailwind CSS Core Concepts](#tailwind-css-core-concepts)
2. [Tailwind CSS v3.4.0 Configuration](#tailwind-css-v340-configuration)
3. [Custom Theme System](#custom-theme-system)
4. [shadcn/ui Philosophy & Patterns](#shadcnui-philosophy--patterns)
5. [clsx + tailwind-merge: The cn() Utility](#clsx--tailwind-merge-the-cn-utility)
6. [Best Practices for AI-Driven Development](#best-practices-for-ai-driven-development)
7. [Component Development Workflow](#component-development-workflow)
8. [Essential Resources](#essential-resources)

---

## Tailwind CSS Core Concepts

### Utility-First Philosophy

Tailwind CSS is a **utility-first** framework that provides low-level utility classes to build custom designs directly in your markup. Instead of writing custom CSS, you compose designs using pre-built utility classes.

**Key Principles:**
- **Composability**: Build complex components from simple utilities
- **Constraint-based**: Work within a consistent design system
- **Responsive by default**: Mobile-first responsive modifiers
- **State variants**: Built-in hover, focus, active, dark mode support

### Class Naming Convention

```html
<!-- Pattern: {property}-{value} -->
<div class="bg-blue-500 text-white p-4 rounded-lg">
  <!-- Background, text color, padding, border radius -->
</div>

<!-- With modifiers: {modifier}:{property}-{value} -->
<button class="hover:bg-blue-600 focus:ring-2 md:text-lg dark:bg-gray-800">
  <!-- Hover, focus, responsive, dark mode -->
</button>
```

### Responsive Design

Tailwind uses a mobile-first breakpoint system:

```javascript
// Default breakpoints
screens: {
  'sm': '640px',   // @media (min-width: 640px)
  'md': '768px',   // @media (min-width: 768px)
  'lg': '1024px',  // @media (min-width: 1024px)
  'xl': '1280px',  // @media (min-width: 1280px)
  '2xl': '1536px', // @media (min-width: 1536px)
}
```

**Usage:**
```html
<div class="text-sm md:text-base lg:text-lg xl:text-xl">
  <!-- Font size increases with screen size -->
</div>
```

### State Variants

```html
<!-- Pseudo-classes -->
<button class="hover:bg-blue-600 focus:ring-2 active:scale-95">

<!-- Dark mode -->
<div class="bg-white dark:bg-gray-900 text-black dark:text-white">

<!-- Group/peer states -->
<div class="group">
  <span class="group-hover:text-blue-500">Hover parent to affect me</span>
</div>
```

---

## Tailwind CSS v3.4.0 Configuration

### Installation

```bash
# Install Tailwind CSS v3.4.0
npm install -D tailwindcss@3.4.0 postcss autoprefixer

# Initialize config
npx tailwindcss init -p
```

### Basic Configuration Structure

**`tailwind.config.js`** (v3.4.0):

```javascript
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,ts,jsx,tsx,mdx}",
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: 'class', // or 'media' for system preference
  theme: {
    extend: {
      // Extend default theme here
    },
  },
  plugins: [],
}
```

### Content Configuration

The `content` array tells Tailwind where to look for class names:

```javascript
content: [
  './pages/**/*.{js,ts,jsx,tsx,mdx}',
  './components/**/*.{js,ts,jsx,tsx,mdx}',
  './app/**/*.{js,ts,jsx,tsx,mdx}',
  './src/**/*.{js,ts,jsx,tsx,mdx}',
]
```

**Important**: Always include all files that contain Tailwind classes to avoid missing utilities in production builds.

### Dark Mode Configuration

```javascript
// Class-based (recommended for manual control)
darkMode: 'class',

// System preference-based
darkMode: 'media',
```

With `class` mode:
```html
<html class="dark">
  <body class="bg-white dark:bg-gray-900">
    <!-- Content -->
  </body>
</html>
```

---

## Custom Theme System

### Theme Extension vs Override

**Extend** (recommended): Add to default theme
```javascript
theme: {
  extend: {
    colors: {
      'brand-primary': '#3b82f6',
      'brand-secondary': '#8b5cf6',
    }
  }
}
```

**Override**: Replace default theme
```javascript
theme: {
  colors: {
    // This replaces ALL default colors
    'primary': '#3b82f6',
  }
}
```

### Custom Colors

```javascript
theme: {
  extend: {
    colors: {
      // Single color
      'brand': '#3b82f6',
      
      // Color palette (recommended)
      'brand': {
        50: '#eff6ff',
        100: '#dbeafe',
        200: '#bfdbfe',
        300: '#93c5fd',
        400: '#60a5fa',
        500: '#3b82f6', // Base color
        600: '#2563eb',
        700: '#1d4ed8',
        800: '#1e40af',
        900: '#1e3a8a',
        950: '#172554',
      },
      
      // Using CSS variables (for dynamic theming)
      'primary': 'var(--color-primary)',
      'secondary': 'var(--color-secondary)',
    }
  }
}
```

**Usage:**
```html
<div class="bg-brand-500 hover:bg-brand-600">
<div class="bg-primary text-secondary">
```

### Custom Fonts

```javascript
theme: {
  extend: {
    fontFamily: {
      sans: ['Inter', 'system-ui', 'sans-serif'],
      serif: ['Merriweather', 'serif'],
      mono: ['Fira Code', 'monospace'],
      display: ['Playfair Display', 'serif'],
    }
  }
}
```

### Custom Spacing

```javascript
theme: {
  extend: {
    spacing: {
      '128': '32rem',
      '144': '36rem',
    }
  }
}
```

### Custom Border Radius

```javascript
theme: {
  extend: {
    borderRadius: {
      '4xl': '2rem',
      '5xl': '3rem',
    }
  }
}
```

### CSS Variables for Dynamic Theming

**`globals.css`**:
```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --color-primary: 59 130 246; /* RGB values for opacity support */
    --color-secondary: 139 92 246;
    --radius: 0.5rem;
  }
  
  .dark {
    --color-primary: 96 165 250;
    --color-secondary: 167 139 250;
  }
}
```

**`tailwind.config.js`**:
```javascript
theme: {
  extend: {
    colors: {
      primary: 'rgb(var(--color-primary) / <alpha-value>)',
      secondary: 'rgb(var(--color-secondary) / <alpha-value>)',
    },
    borderRadius: {
      DEFAULT: 'var(--radius)',
    }
  }
}
```

---

## shadcn/ui Philosophy & Patterns

### What is shadcn/ui?

**shadcn/ui is NOT a component library**. It's a **code distribution system** that provides:

- ✅ **Copy-paste components**: You own the code
- ✅ **Open source**: Full transparency and customization
- ✅ **Composable**: Consistent API across components
- ✅ **Accessible**: Built on Radix UI primitives
- ✅ **Beautiful defaults**: Production-ready styling
- ✅ **AI-ready**: Open code for LLMs to understand

### Core Principles

1. **Open Code**: You get the actual component source code
2. **Full Control**: Modify any part to fit your needs
3. **Composition**: Common interface across all components
4. **No npm Package**: Components live in your codebase
5. **Radix UI Foundation**: Accessibility and functionality from Radix primitives

### Installation & CLI

```bash
# Install shadcn/ui CLI
npx shadcn-ui@latest init

# Add components
npx shadcn-ui@latest add button
npx shadcn-ui@latest add card
npx shadcn-ui@latest add dialog
```

### Component Structure

All shadcn/ui components follow this pattern:

```tsx
// components/ui/button.tsx
import * as React from "react"
import { cn } from "@/lib/utils"

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "default" | "destructive" | "outline" | "ghost"
  size?: "default" | "sm" | "lg" | "icon"
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "default", size = "default", ...props }, ref) => {
    return (
      <button
        className={cn(
          "inline-flex items-center justify-center rounded-md",
          "focus-visible:outline-none focus-visible:ring-2",
          {
            "bg-primary text-primary-foreground": variant === "default",
            "bg-destructive text-destructive-foreground": variant === "destructive",
          },
          className
        )}
        ref={ref}
        {...props}
      />
    )
  }
)
Button.displayName = "Button"

export { Button }
```

### Key Patterns

#### 1. Forwarded Refs
All components use `React.forwardRef` for ref forwarding:
```tsx
const Component = React.forwardRef<HTMLElement, Props>((props, ref) => {
  return <element ref={ref} {...props} />
})
```

#### 2. Variant Props
Components use variant props for styling variations:
```tsx
type ButtonProps = {
  variant?: "default" | "destructive" | "outline"
  size?: "sm" | "md" | "lg"
}
```

#### 3. ClassName Merging
Always merge passed className with default classes using `cn()`:
```tsx
<button className={cn("base-classes", className)} />
```

#### 4. Composition with Radix UI
Components compose Radix primitives:
```tsx
import * as DialogPrimitive from "@radix-ui/react-dialog"

const Dialog = DialogPrimitive.Root
const DialogTrigger = DialogPrimitive.Trigger
// ... more exports
```

### Component Anatomy Example

**Dialog Component Structure:**
```tsx
// Primitive wrapper
const Dialog = DialogPrimitive.Root

// Styled components
const DialogContent = React.forwardRef<...>(({ className, children, ...props }, ref) => (
  <DialogPrimitive.Portal>
    <DialogPrimitive.Overlay className={cn("overlay-classes")} />
    <DialogPrimitive.Content
      ref={ref}
      className={cn("content-classes", className)}
      {...props}
    >
      {children}
    </DialogPrimitive.Content>
  </DialogPrimitive.Portal>
))

// Export pattern
export {
  Dialog,
  DialogTrigger,
  DialogContent,
  DialogHeader,
  DialogFooter,
  DialogTitle,
  DialogDescription,
}
```

### Customization Strategy

Since you own the code, modify components directly:

```tsx
// components/ui/button.tsx - Customize as needed
const buttonVariants = cva(
  "base-button-classes",
  {
    variants: {
      variant: {
        default: "bg-primary hover:bg-primary/90",
        destructive: "bg-red-500 hover:bg-red-600",
        // Add your own variants
        gradient: "bg-gradient-to-r from-blue-500 to-purple-500",
      }
    }
  }
)
```

---

## clsx + tailwind-merge: The cn() Utility

### The Problem

Tailwind classes can conflict when merging:

```jsx
// ❌ Problem: Which background wins?
<button className="bg-blue-500 bg-red-500">
  // Result is unpredictable!
</button>

// ❌ Problem: Dynamic classes
<button className={`bg-blue-500 ${isError ? 'bg-red-500' : ''}`}>
  // bg-blue-500 and bg-red-500 both applied!
</button>
```

### The Solution: cn() Utility

**`lib/utils.ts`**:
```typescript
import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
```

### How It Works

1. **clsx**: Handles conditional class logic
2. **twMerge**: Intelligently merges Tailwind classes (last class wins)

```typescript
// clsx handles conditionals
clsx('text-white', { 'bg-blue-500': true, 'bg-red-500': false })
// → 'text-white bg-blue-500'

// twMerge resolves conflicts
twMerge('bg-blue-500 bg-red-500')
// → 'bg-red-500' (last wins)

// cn() does both
cn('bg-blue-500', { 'bg-red-500': isError })
// → 'bg-red-500' if isError, otherwise 'bg-blue-500'
```

### Usage Patterns

#### Basic Merging
```tsx
cn('px-4 py-2 rounded', className)
// Merges base classes with passed className
```

#### Conditional Classes
```tsx
cn(
  'base-classes',
  {
    'bg-blue-500': !isPending,
    'bg-gray-500': isPending,
    'cursor-not-allowed': isDisabled,
  }
)
```

#### Complex Conditions
```tsx
cn(
  'text-white px-4 py-2 rounded',
  isPending && 'bg-gray-500 cursor-wait',
  isError && 'bg-red-500',
  !isPending && !isError && 'bg-blue-500 hover:bg-blue-600',
  className
)
```

#### Component Props
```tsx
interface ButtonProps {
  variant?: 'primary' | 'secondary'
  size?: 'sm' | 'lg'
  className?: string
}

function Button({ variant = 'primary', size = 'sm', className, ...props }: ButtonProps) {
  return (
    <button
      className={cn(
        'rounded font-medium transition-colors',
        {
          'bg-blue-500 hover:bg-blue-600': variant === 'primary',
          'bg-gray-500 hover:bg-gray-600': variant === 'secondary',
          'px-3 py-1 text-sm': size === 'sm',
          'px-6 py-3 text-lg': size === 'lg',
        },
        className // Always last to allow overrides
      )}
      {...props}
    />
  )
}
```

### Best Practices

1. ✅ **Always use cn() for class merging** in components
2. ✅ **Put className prop last** to allow consumer overrides
3. ✅ **Use object syntax** for readability with conditionals
4. ✅ **Avoid string concatenation** - use cn() instead
5. ✅ **Group related classes** for better organization

```tsx
// ❌ Don't do this
className={`${baseClasses} ${isActive ? activeClasses : ''}`}

// ✅ Do this
className={cn(baseClasses, isActive && activeClasses)}
```

---

## Best Practices for AI-Driven Development

### 1. Component Design Patterns

#### Atomic Design Approach
```
atoms/       → Button, Input, Label
molecules/   → FormField, Card, SearchBar
organisms/   → Header, Form, DataTable
templates/   → PageLayout, DashboardLayout
pages/       → HomePage, ProfilePage
```

#### Component Anatomy Template
```tsx
import * as React from "react"
import { cn } from "@/lib/utils"

// 1. Type definitions
interface ComponentProps
  extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "alternative"
}

// 2. Component with forwardRef
const Component = React.forwardRef<HTMLDivElement, ComponentProps>(
  ({ className, variant = "default", children, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          // Base styles
          "base-classes",
          // Variants
          {
            "variant-classes": variant === "default",
            "alt-variant-classes": variant === "alternative",
          },
          // User overrides (always last)
          className
        )}
        {...props}
      >
        {children}
      </div>
    )
  }
)

// 3. Display name for dev tools
Component.displayName = "Component"

// 4. Export
export { Component }
export type { ComponentProps }
```

### 2. Responsive Design Strategy

Use mobile-first approach:
```tsx
<div className={cn(
  // Mobile (default)
  "flex flex-col gap-2 p-4",
  // Tablet
  "md:flex-row md:gap-4 md:p-6",
  // Desktop
  "lg:gap-6 lg:p-8",
  // Large screens
  "xl:max-w-7xl xl:mx-auto"
)}>
```

### 3. Accessibility Checklist

- ✅ Use semantic HTML elements
- ✅ Include ARIA labels where needed
- ✅ Ensure keyboard navigation works
- ✅ Provide focus styles
- ✅ Use proper heading hierarchy
- ✅ Include alt text for images
- ✅ Use Radix UI primitives (via shadcn/ui)

```tsx
<button
  className={cn("...")}
  aria-label="Close dialog"
  aria-expanded={isOpen}
>
```

### 4. Performance Optimization

#### Avoid Dynamic Classes
```tsx
// ❌ Bad - Creates new classes at runtime
<div className={`bg-${color}-500`}> 

// ✅ Good - Use predefined classes with cn()
<div className={cn({
  'bg-blue-500': color === 'blue',
  'bg-red-500': color === 'red',
})}>
```

#### Use Tailwind's Arbitrary Values Sparingly
```tsx
// ⚠️ Use only when necessary
<div className="w-[137px]">

// ✅ Prefer theme values
<div className="w-32"> // 8rem = 128px
```

### 5. Code Organization

```
src/
├── components/
│   ├── ui/              # shadcn/ui components
│   │   ├── button.tsx
│   │   ├── dialog.tsx
│   │   └── ...
│   ├── atoms/           # Basic components
│   ├── molecules/       # Composite components
│   └── organisms/       # Complex components
├── lib/
│   └── utils.ts         # cn() utility
├── styles/
│   └── globals.css      # Tailwind directives
└── app/                 # Next.js app directory
```

---

## Component Development Workflow

### 1. Planning Phase

Before implementing:
- ✅ Identify component variants and states
- ✅ List required props and types
- ✅ Consider accessibility requirements
- ✅ Plan responsive behavior
- ✅ Check if shadcn/ui component exists

### 2. Implementation Checklist

```tsx
// ✅ Import dependencies
import * as React from "react"
import { cn } from "@/lib/utils"

// ✅ Define types
interface Props extends React.HTMLAttributes<HTMLElement> {
  // Component-specific props
}

// ✅ Implement component with forwardRef
const Component = React.forwardRef<HTMLElement, Props>(
  ({ className, ...props }, ref) => {
    // ✅ Use cn() for class merging
    return <element className={cn("...", className)} ref={ref} {...props} />
  }
)

// ✅ Set display name
Component.displayName = "Component"

// ✅ Export component and types
export { Component }
export type { Props as ComponentProps }
```

### 3. Testing Checklist

- ✅ Test all variants
- ✅ Test responsive breakpoints
- ✅ Test dark mode
- ✅ Test keyboard navigation
- ✅ Test with screen reader (if applicable)
- ✅ Test className override
- ✅ Verify ref forwarding

### 4. Common Patterns

#### Form Field with Error State
```tsx
<div className={cn("space-y-2")}>
  <Label htmlFor="email">Email</Label>
  <Input
    id="email"
    type="email"
    className={cn(errors.email && "border-red-500")}
  />
  {errors.email && (
    <p className="text-sm text-red-500">{errors.email}</p>
  )}
</div>
```

#### Loading States
```tsx
<Button
  disabled={isLoading}
  className={cn(isLoading && "opacity-50 cursor-not-allowed")}
>
  {isLoading ? <Spinner /> : "Submit"}
</Button>
```

#### Conditional Rendering
```tsx
{isVisible && (
  <Alert variant="destructive">
    <AlertTitle>Error</AlertTitle>
    <AlertDescription>{errorMessage}</AlertDescription>
  </Alert>
)}
```

---

## Essential Resources

### Official Documentation

#### Tailwind CSS
- **Main Docs**: https://tailwindcss.com/docs
- **v3 Docs**: https://v3.tailwindcss.com/docs
- **Installation**: https://tailwindcss.com/docs/installation
- **Configuration**: https://v3.tailwindcss.com/docs/configuration
- **Theme**: https://v3.tailwindcss.com/docs/theme
- **Customizing**: https://tailwindcss.com/docs/adding-custom-styles
- **GitHub**: https://github.com/tailwindlabs/tailwindcss

#### shadcn/ui
- **Main Site**: https://ui.shadcn.com
- **Components**: https://ui.shadcn.com/docs/components
- **Installation**: https://ui.shadcn.com/docs/installation
- **Theming**: https://ui.shadcn.com/docs/theming
- **CLI**: https://ui.shadcn.com/docs/cli
- **GitHub**: https://github.com/shadcn-ui/ui

#### Radix UI (Foundation of shadcn/ui)
- **Docs**: https://www.radix-ui.com/primitives/docs/overview/introduction
- **Primitives**: https://www.radix-ui.com/primitives

### Utility Libraries

#### clsx
- **npm**: https://www.npmjs.com/package/clsx
- **GitHub**: https://github.com/lukeed/clsx

#### tailwind-merge
- **npm**: https://www.npmjs.com/package/tailwind-merge
- **GitHub**: https://github.com/dcastil/tailwind-merge

### Learning Resources

#### Articles & Guides
- **Mastering Tailwind CSS**: https://dev.to/sheraz4194/mastering-tailwind-css-overcome-styling-conflicts-with-tailwind-merge-and-clsx-1dol
- **shadcn/ui Tutorial**: https://codeparrot.ai/blogs/shadcn-ui-for-beginners-the-ultimate-guide-and-step-by-step-tutorial
- **Custom Themes**: https://blog.logrocket.com/creating-custom-themes-tailwind-css/
- **Theme Customization**: https://www.locofy.ai/blog/create-a-custom-theme-with-tailwindcss

#### Stack Overflow
- **Tailwind + clsx**: https://stackoverflow.com/questions/69390216/how-to-properly-join-tailwind-css-classes-using-clsx

### Design Systems

#### Color Palette Tools
- **Tailwind Colors**: https://tailwindcss.com/docs/customizing-colors
- **UI Colors**: https://uicolors.app/create

#### Component Libraries (for reference)
- **Tailwind UI**: https://tailwindui.com
- **Flowbite**: https://flowbite.com
- **Headless UI**: https://headlessui.com

---

## Quick Reference: Common Patterns

### Layout
```html
<!-- Flex Container -->
<div class="flex flex-col md:flex-row gap-4 items-center justify-between">

<!-- Grid -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">

<!-- Container -->
<div class="container mx-auto px-4 max-w-7xl">
```

### Typography
```html
<h1 class="text-3xl md:text-4xl lg:text-5xl font-bold">
<p class="text-sm md:text-base text-gray-600 dark:text-gray-400">
```

### Spacing
```html
<!-- Padding: p-{size}, px-{size}, py-{size} -->
<div class="p-4 px-6 py-8">

<!-- Margin: m-{size}, mx-{size}, my-{size} -->
<div class="m-4 mx-auto my-8">

<!-- Gap: gap-{size} -->
<div class="flex gap-4">
```

### Colors
```html
<!-- Background -->
<div class="bg-blue-500 hover:bg-blue-600 dark:bg-blue-700">

<!-- Text -->
<p class="text-gray-900 dark:text-white">

<!-- Border -->
<div class="border-2 border-gray-200 dark:border-gray-700">
```

### Shadows & Effects
```html
<div class="shadow-sm hover:shadow-lg transition-shadow">
<div class="rounded-lg backdrop-blur-sm bg-white/80">
```

---

## Version Notes

### Tailwind CSS v3 vs v4

**v3.4.0 (Current - Stable)**:
- ✅ Uses `tailwind.config.js`
- ✅ Mature ecosystem
- ✅ All shadcn/ui components compatible
- ✅ Extensive documentation

**v4.0 (Latest - Beta)**:
- 🆕 CSS-first configuration (`@theme` directive)
- 🆕 Native CSS variables
- 🆕 Improved performance
- ⚠️ Breaking changes from v3
- ⚠️ Migration required

**Recommendation**: Stick with **v3.4.0** for production projects until v4 is stable and ecosystem catches up.

---

## Conclusion

This guide provides a comprehensive foundation for building modern UX/UI with Tailwind CSS and shadcn/ui. Remember:

1. **Use utility-first** approach with Tailwind
2. **Leverage shadcn/ui** for production-ready components
3. **Always use cn()** for class merging
4. **Customize freely** - you own the code
5. **Follow patterns** for consistency
6. **Prioritize accessibility** in every component

Happy building! 🚀