# Tailwind CSS Setup for Pulse

This document explains how Tailwind CSS is configured and how to work with it in the Pulse Django application.

## 🎨 Overview

Pulse uses Tailwind CSS 3.4+ with custom configurations and components for a professional healthcare interface.

## 📁 File Structure

```
Pulse/
├── package.json              # Node.js dependencies and scripts
├── tailwind.config.js        # Tailwind configuration
├── static/css/
│   ├── input.css             # Source CSS file with Tailwind directives
│   └── output.css            # Generated CSS file (git-ignored)
├── templates/base.html       # Base template that includes output.css
└── dev.sh                    # Development script
```

## 🚀 Quick Start

### Option 1: Use the Development Script (Recommended)
```bash
./dev.sh
```
This starts both Django and Tailwind in watch mode.

### Option 2: Manual Setup
```bash
# Terminal 1: Start Tailwind CSS compiler
npm run dev

# Terminal 2: Start Django server
source venv/bin/activate
python manage.py runserver
```

## 📦 Available npm Scripts

- `npm run dev` - Start Tailwind in watch mode (development)
- `npm run build` - Build production CSS (minified)
- `npm run build-css` - Alias for dev (watch mode)
- `npm run build-css-prod` - Alias for build (production)

## 🎨 Custom Components

The `static/css/input.css` file includes custom Tailwind components:

### Cards
```html
<div class="card">
  <div class="card-header">
    <h3 class="card-title">Title</h3>
  </div>
  <div class="card-body">
    Content here
  </div>
</div>
```

### Buttons
```html
<button class="btn btn-primary">Primary Button</button>
<button class="btn btn-secondary">Secondary Button</button>
<button class="btn btn-success">Success Button</button>
```

### Forms
```html
<label class="form-label">Label</label>
<input class="form-input" type="text">
<select class="form-select">
  <option>Option 1</option>
</select>
```

### Badges & Alerts
```html
<span class="badge badge-primary">Badge</span>
<div class="alert alert-success">Success message</div>
```

### Research Components
```html
<div class="research-card">
  <div class="research-meta">
    <span class="specialty-tag">Cardiology</span>
    <span class="date-tag">2024-01-01</span>
    <span class="relevance-tag">9.5</span>
  </div>
</div>
```

## 🎯 Custom Brand Colors

```javascript
// Primary blues
primary-50 to primary-900

// Secondary grays
secondary-50 to secondary-900

// Success greens
success-50 to success-900

// Warning yellows
warning-50 to warning-900

// Error reds
error-50 to error-900
```

## 🔧 Configuration Highlights

### Content Sources
Tailwind scans these files for classes:
- `./templates/**/*.html`
- `./core/templates/**/*.html`
- `./static/js/**/*.js`
- `./**/*.py`

### Plugins
- `@tailwindcss/forms` - Better form styling
- `@tailwindcss/typography` - Rich text styling

### Custom Animations
- `animate-fade-in` - Fade in effect
- `animate-slide-up` - Slide up effect
- `animate-pulse-slow` - Slow pulse effect

## 🛠 Development Workflow

1. **Start Development**: Run `./dev.sh` or use manual setup
2. **Edit Templates**: Add Tailwind classes to your HTML templates
3. **Custom Styles**: Modify `static/css/input.css` for custom components
4. **Auto-Rebuild**: Tailwind automatically rebuilds CSS when files change

## 📱 Production Deployment

For production, build the minified CSS:

```bash
npm run build
```

This creates an optimized `static/css/output.css` file with only the CSS classes actually used in your templates.

## 🐛 Troubleshooting

### CSS Not Loading
- Check that `static/css/output.css` exists
- Verify `STATIC_URL` settings in Django
- Run `npm run build` to generate CSS

### Classes Not Working
- Ensure Tailwind is scanning your template files
- Check `tailwind.config.js` content paths
- Restart the Tailwind compiler

### Performance Issues
- Use production build for deployment
- Check if unnecessary classes are being included
- Consider purging unused CSS

## 📚 Resources

- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Tailwind Forms Plugin](https://github.com/tailwindlabs/tailwindcss-forms)
- [Django Static Files](https://docs.djangoproject.com/en/stable/howto/static-files/)

## 🎉 Ready to Use

The setup is complete and ready for development! Your custom components and brand colors are configured for a professional healthcare application interface.