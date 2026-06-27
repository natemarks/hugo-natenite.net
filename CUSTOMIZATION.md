# Customization Guide

## Homepage Title Color Override

The homepage h1 title ("Expert AWS Operations & Governance") is styled in the primary theme color (#4682B4, steel blue) instead of the default black.

### How It Works

**1. Custom CSS File: `static/css/custom.css`**
```css
.page-home .intro h1 {
  color: #4682B4 !important;
}
```

- **`.page-home`** - Targets only the homepage (Hugo adds this class to the body)
- **`.intro h1`** - Targets the h1 element in the intro section
- **`!important`** - Overrides the theme's default `color: $black` rule in `themes/hugo-serif-theme/assets/scss/components/_intro.scss`
- **`#4682B4`** - Steel blue color (matches `config.toml` primary color)

**2. Base Template Override: `layouts/_default/baseof.html`**

Line 22 loads the custom CSS:
```html
<!-- Custom CSS -->
<link rel="stylesheet" href="{{ "css/custom.css" | relURL }}">
```

This template file overrides the theme's `baseof.html` to add the custom CSS link after the theme's compiled SCSS, ensuring our custom styles take precedence.

### Why This Approach?

- **Simple**: Just a static CSS file with hardcoded color
- **No SCSS complications**: Avoids issues with importing template-processed SCSS files
- **Maintainable**: Easy to modify the color by editing `static/css/custom.css`
- **Specific**: Only affects the homepage h1, not other headings

### To Change the Color

Edit `static/css/custom.css` and change `#4682B4` to your desired hex color. Remember to update `config.toml` primary color if you want consistency across buttons, links, etc.
