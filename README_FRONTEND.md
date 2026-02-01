# BoostSync Frontend

A complete frontend clone of boostsync.mysellauth.com built with Next.js, React, and TypeScript.

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **Utilities**: clsx, tailwind-merge

## Project Structure

```
/home/engine/project/
├── app/                          # Next.js App Router
│   ├── api/                      # API routes (placeholder for backend)
│   │   ├── auth/
│   │   │   ├── login/
│   │   │   ├── register/
│   │   │   └── forgot-password/
│   │   └── dashboard/
│   ├── dashboard/                # Dashboard pages
│   ├── forgot-password/          # Password reset page
│   ├── login/                    # Login page
│   ├── signup/                   # Signup page
│   ├── globals.css              # Global styles
│   ├── layout.tsx               # Root layout
│   └── page.tsx                 # Home page
├── components/
│   ├── layout/
│   │   ├── Header.tsx           # Navigation header
│   │   └── Footer.tsx           # Footer
│   └── home/
│       ├── HeroSection.tsx      # Hero section
│       ├── FeaturesSection.tsx  # Features grid
│       ├── PricingSection.tsx   # Pricing plans
│       ├── TestimonialsSection.tsx # Testimonials
│       └── CTASection.tsx       # Call-to-action
├── lib/
│   ├── types.ts                 # TypeScript type definitions
│   └── utils.ts                 # Utility functions
├── services/                    # API service layer
│   ├── api.ts                   # API client configuration
│   ├── auth.service.ts          # Authentication service
│   ├── dashboard.service.ts     # Dashboard service
│   ├── boost.service.ts         # Boost service
│   └── index.ts                 # Service exports
├── .env.local                   # Environment variables
├── next.config.js               # Next.js configuration
├── tailwind.config.ts           # Tailwind CSS configuration
├── tsconfig.json                # TypeScript configuration
└── package.json                 # Dependencies
```

## Features Implemented

### Pages
- ✅ Home/Landing page
  - Hero section with CTAs
  - Features overview
  - Pricing plans
  - Testimonials
  - Final CTA section
- ✅ Authentication pages
  - Login
  - Signup
  - Forgot password
- ✅ Dashboard page
  - Statistics overview
  - Quick actions
  - Recent activity
  - Upcoming events

### Components
- ✅ Responsive Header with navigation
- ✅ Footer with links and social media
- ✅ Modular, reusable components
- ✅ Mobile-first responsive design

### Services (Ready for Backend Integration)
- ✅ API client with authentication
- ✅ Auth service (login, register, password reset)
- ✅ Dashboard service (stats, activity, servers)
- ✅ Boost service (packages, purchases)

### Types
- ✅ Complete TypeScript type definitions
- ✅ API response types
- ✅ User, Server, Boost types

## Getting Started

### Installation

```bash
# Install dependencies
npm install

# or
yarn install

# or
pnpm install
```

### Environment Setup

Create a `.env.local` file in the root directory:

```env
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:3001/api
NEXT_PUBLIC_APP_URL=http://localhost:3000

# Authentication
NEXT_PUBLIC_ENABLE_AUTH=true

# Application Settings
NEXT_PUBLIC_APP_NAME=BoostSync
NEXT_PUBLIC_APP_DESCRIPTION=Boost your Discord server with premium features
```

### Development

```bash
# Start development server
npm run dev

# or
yarn dev

# or
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Build

```bash
# Build for production
npm run build

# or
yarn build

# or
pnpm build
```

### Production

```bash
# Start production server
npm start

# or
yarn start

# or
pnpm start
```

## API Integration

The frontend is ready for backend integration. All service methods are structured to work with a REST API.

### Example: Connecting to a Backend

1. Update `NEXT_PUBLIC_API_URL` in `.env.local` to your backend URL
2. Implement the API route handlers in `app/api/`
3. The service layer will automatically handle requests to your backend

### Service Usage Examples

```typescript
import { authService } from '@/services';

// Login
const response = await authService.login({
  email: 'user@example.com',
  password: 'password123'
});

if (response.success) {
  const { user, token } = response.data;
  authService.setAuthData(token, user);
}

// Get dashboard stats
import { dashboardService } from '@/services';

const statsResponse = await dashboardService.getStats();
if (statsResponse.success) {
  console.log(statsResponse.data);
}
```

## Styling

The project uses Tailwind CSS for styling. The configuration is in `tailwind.config.ts`.

### Custom Colors

Primary colors are defined in the Tailwind config:
- `primary-50` to `primary-900` gradient shades

### Utility Classes

- Use `cn()` from `@/lib/utils` for conditional class merging
- Example: `cn("base-class", condition && "conditional-class")`

## Responsive Design

All components are built with a mobile-first approach:
- Mobile: < 768px
- Tablet: 768px - 1024px
- Desktop: > 1024px

## Type Safety

The entire codebase is written in TypeScript with strict type checking enabled. All API responses, props, and state are fully typed.

## Best Practices Used

1. **Component Modularity**: Each component is self-contained and reusable
2. **Type Safety**: Full TypeScript implementation
3. **API Service Layer**: Clean separation of API calls
4. **Environment Configuration**: Secure environment variable handling
5. **Responsive Design**: Mobile-first approach with Tailwind CSS
6. **Error Handling**: Consistent error handling across API calls
7. **Accessibility**: Proper semantic HTML and ARIA labels
8. **Performance**: Optimized images, lazy loading, and code splitting

## Future Enhancements

- [ ] Connect API routes to actual backend
- [ ] Implement authentication flow
- [ ] Add form validation
- [ ] Implement loading states
- [ ] Add error boundary
- [ ] Set up analytics
- [ ] Add unit tests
- [ ] Add E2E tests
- [ ] Implement i18n for multi-language support

## License

This project is part of BoostSync.
