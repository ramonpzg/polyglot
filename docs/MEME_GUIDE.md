# Meme & GIF Integration Guide

## Quick Reference

This presentation is set up with proper meme/gif placeholders and overflow fixes. Here's how to use them.

## Using the MemeSlot Component

Replace any meme placeholder in the slides with the MemeSlot component:

```vue
<!-- Basic meme placeholder -->
<MemeSlot 
  type="meme"
  title="Drake Meme"
  description="❌ Writing everything in Python"
  caption="✅ Using Python as the orchestrator"
/>

<!-- GIF placeholder -->
<MemeSlot 
  type="gif"
  title="Loading Bar"
  description="Actual 32-second Python execution"
  :animated="true"
/>

<!-- With actual image -->
<MemeSlot 
  type="meme"
  src="/images/friendship-ended.jpg"
  alt="Friendship ended with pip"
  footer="Now uv is my best friend"
/>

<!-- New Yorker style cartoon -->
<MemeSlot 
  type="cartoon"
  title="Python at desk"
  description="Python in a suit watching other languages exercise"
  caption="'I'm more of a manager these days'"
/>

<!-- QR Code -->
<MemeSlot 
  type="qr"
  title="Resources"
  description="github.com/pycon-au/polyglot-examples"
/>
```

## Meme Suggestions by Slide

### Slide 4: Python as Manager
- **Type**: New Yorker cartoon
- **Scene**: Python in business suit at desk, other languages doing pushups
- **Caption**: "I'm more of a ideas language"

### Slide 6: Language Poll
- **Type**: GIF
- **Scene**: Developer debugging JavaScript
- **Text**: "undefined is not a function" error loop

### Slide 7: AI Optimization
- **Type**: Meme template
- **Format**: "We have optimization at home"
- **Punchline**: *optimization at home: @lru_cache*

### Slide 11: Browser Python
- **Type**: Drake meme
- **Top**: Running Python natively
- **Bottom**: 50MB WASM download

### Slide 19: Rust Revolution
- **Type**: Friendship ended meme
- **Text**: "Friendship ended with pip, now uv is my best friend"

### Slide 29: C++ Reality
- **Type**: Scooby Doo mask reveal
- **Scene**: Pulling off Python mask to reveal C++
- **Text**: "It was C++ all along!"

### Slide 31: Python Performance
- **Type**: Animated GIF
- **Scene**: Actual 32-second loading bar
- **Note**: Not sped up, actually takes 32 seconds

### Slide 36: Zig Evolution
- **Type**: Pokemon evolution meme
- **Evolution**: C → C++ (messier) → Zig (clean)

### Slide 42: Job Security
- **Type**: Stonks meme
- **Text**: "Job Security"
- **Context**: When AI can't debug its own code

## Generating Memes

### AI Generation Prompts

For New Yorker style cartoons:
```
Create a single-panel cartoon in New Yorker style:
- Python as office manager in suit
- Rust, C++, Zig as workers exercising
- Minimalist black and white line art
- Caption: "I'm more of an ideas language"
```

For technical memes:
```
Create a Drake meme template:
- Top panel: "Writing everything in Python" (disapproval)
- Bottom panel: "Using Python to orchestrate fast languages" (approval)
```

### Free Resources
- imgflip.com - Meme generator
- makeameme.org - Quick templates
- giphy.com - GIF search
- quickmeme.com - Classic formats

## Overflow Fixes Applied

The presentation now includes:

1. **Global overflow handling**: All slides are scrollable if content exceeds viewport
2. **Component constraints**: Terminal demos, polls, and charts have max-heights
3. **Responsive grids**: Bingo and other grids adapt to screen size
4. **Code block scrolling**: Long code blocks are scrollable
5. **Meme placeholders**: Clearly marked spots for visual content

## Adding Your Own Images

1. Create an `images/` directory in the project root
2. Add your memes/gifs there
3. Reference them in MemeSlot components:

```vue
<MemeSlot 
  type="meme"
  src="/images/your-meme.jpg"
  alt="Description for accessibility"
/>
```

## Animation Ideas

### Slide Transitions
- Python snake transforming into Rust crab (slide 19)
- Loading bars that actually take the stated time
- Code particles forming into language logos
- Benchmark bars racing in real-time

### Interactive Elements
- Click-to-reveal performance numbers
- Hover to show language details
- Drag-and-drop language comparisons
- Live typing animations in terminal demos

## Performance Tips

1. **Optimize images**: Keep memes under 500KB
2. **Lazy load**: Use v-show for conditional rendering
3. **Preload critical**: Add key memes to public folder
4. **GIF alternatives**: Consider CSS animations for simple loops

## Troubleshooting

### Content Cut Off
- Check `style.css` is imported
- Ensure slidev-layout has overflow-y: auto
- Verify max-height constraints on components

### Memes Not Loading
- Check file paths (relative to public/)
- Verify image formats (jpg, png, gif, webp)
- Test with placeholder first

### Placeholders Too Large
- Adjust max-width in MemeSlot component
- Use type-specific sizing (qr=300px, meme=600px)
- Consider grid layout for multiple memes

## Quick Fixes

```css
/* Force slide to be scrollable */
.slidev-layout {
  overflow-y: auto !important;
  max-height: 100vh !important;
}

/* Fix component overflow */
.your-component {
  max-height: 70vh;
  overflow-y: auto;
}

/* Ensure memes don't break layout */
.meme-slot img {
  max-width: 100%;
  height: auto;
}
```

## Export Considerations

When exporting to PDF:
1. Meme placeholders will show as designed
2. Actual images will be embedded
3. GIFs become static first frames
4. Interactive elements show default state

## License & Attribution

Remember to:
- Credit meme creators where known
- Use royalty-free images for commercial talks
- Check conference guidelines on humor
- Keep backups of all visual content