# Agents Guide for Polyglot Project

## Overview
Polyglot presentation using Slidev (Vue-based slides) demonstrating Python integration with multiple languages (Rust, C++, Zig, etc.). Contains live demo projects and code examples.

## Commands
- **Dev**: `bun dev` - Start Slidev dev server at localhost:3030
- **Build**: `bun run build` - Build slides for production
- **Export**: `bun run export` - Export slides to PDF

## Architecture
- **slides.md**: Main presentation content (Slidev markdown with Vue components)
- **components/**: Vue components for interactive demos (BushfireDemo.vue, CaribeTechDemo.vue, etc.)
- **projects/**: Full demo applications (bushfire-sim, outback-monitor, caribetech, etc.) - Python+Rust/FFI examples
- **examples/**: Language integration examples (rust/, cpp/, zig/, jspython/, etc.)
- **Python projects** use maturin for Rust bindings with FastAPI servers
- **No formal tests** - this is a presentation repository

## Code Style
- **Slidev**: Vue 3 composition API, TypeScript for utilities
- **Python**: Modern Python 3.12+, FastAPI for servers, Click for CLIs
- **Rust**: PyO3/maturin for Python bindings, standard Rust conventions
- **Vue components**: Script setup syntax, concise template structure
- **No linting/formatting** configured - this is demo/presentation code
