# SentinelDF Landing Page

Modern, conversion-optimized landing page for SentinelDF SaaS product.

## Quick Start

```bash
# Install dependencies
cd landing-page
npm install

# Run development server
npm run dev

# Open http://localhost:3000
```

## Tech Stack

- **Framework:** Next.js 14 (App Router)
- **Styling:** TailwindCSS + shadcn/ui
- **Animations:** Framer Motion
- **Forms:** React Hook Form + Zod
- **Analytics:** PostHog (optional)
- **Deployment:** Vercel (one-click deploy)

## Project Structure

```
landing-page/
├── app/
│   ├── layout.tsx          # Root layout
│   ├── page.tsx            # Homepage
│   └── globals.css         # Global styles
├── components/
│   ├── hero.tsx            # Hero section
│   ├── problem.tsx         # Problem section
│   ├── solution.tsx        # Solution section
│   ├── features.tsx        # Features grid
│   ├── demo.tsx            # Interactive demo
│   ├── pricing.tsx         # Pricing table
│   ├── testimonials.tsx    # Social proof
│   ├── cta.tsx             # Call-to-action
│   └── footer.tsx          # Footer
├── public/
│   ├── images/             # Images and diagrams
│   └── favicon.ico         # Favicon
├── package.json
├── tailwind.config.ts
└── next.config.js
```

## Features

✅ Responsive design (mobile-first)  
✅ Dark mode support  
✅ SEO optimized (meta tags, Open Graph)  
✅ Fast loading (90+ Lighthouse score)  
✅ Interactive demo (live API integration)  
✅ Conversion tracking (PostHog)  

## Deployment

### Vercel (Recommended)

1. Push code to GitHub
2. Import repo to Vercel
3. Deploy automatically
4. Add custom domain (sentineldf.com)

### Manual

```bash
# Build for production
npm run build

# Start production server
npm start
```

## Environment Variables

Create `.env.local`:

```bash
# API endpoint (for demo)
NEXT_PUBLIC_API_URL=https://api.sentineldf.com

# Analytics (optional)
NEXT_PUBLIC_POSTHOG_KEY=phc_...
NEXT_PUBLIC_POSTHOG_HOST=https://app.posthog.com

# Stripe (for checkout)
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_live_...
```

## Customization

Edit `app/page.tsx` to change content.  
Edit `components/*.tsx` to modify sections.  
Edit `tailwind.config.ts` for colors/fonts.

## License

Apache 2.0 - See LICENSE file.
