## 1. Design System Foundation

- [ ] 1.1 Add CSS custom properties for colors (primary, secondary, accent, background, surface, text, semantic) to global CSS
- [ ] 1.2 Add CSS custom properties for typography (font families, sizes, weights, line heights)
- [ ] 1.3 Add CSS custom properties for spacing scale
- [ ] 1.4 Add CSS custom properties for border radius values
- [ ] 1.5 Update Tailwind config to reference design tokens

## 2. Unified Navigation

- [ ] 2.1 Update AppNav.tsx to always render (remove conditional hiding)
- [ ] 2.2 Add hamburger menu icon for mobile viewport (< 768px)
- [ ] 2.3 Implement bottom sheet mobile menu with all navigation links
- [ ] 2.4 Add close button and tap-outside-to-close behavior
- [ ] 2.5 Add active link highlighting based on current path

## 3. Page Header Cleanup

- [ ] 3.1 Identify pages with custom headers (not using AppNav)
- [ ] 3.2 Remove custom headers from affected pages
- [ ] 3.3 Ensure all 8 pages use AppNav consistently

## 4. Responsive Layout Updates

- [ ] 4.1 Verify/fix responsive grid on home page (/)
- [ ] 4.2 Verify/fix responsive grid on favorites page (/favorites)
- [ ] 4.3 Verify/fix responsive grid on monitor page (/monitor)
- [ ] 4.4 Verify/fix responsive grid on kanban page (/kanban)
- [ ] 4.5 Verify/fix responsive grid on lab page (/lab)
- [ ] 4.6 Verify/fix responsive grid on arbitrage page (/arbitrage)
- [ ] 4.7 Verify/fix responsive grid on combo select page (/combo/select)
- [ ] 4.8 Verify/fix responsive grid on external balances page (/external/balances)

## 5. Page-Specific Color Updates

- [ ] 5.1 Update home page to use design tokens
- [ ] 5.2 Update favorites page to use design tokens
- [ ] 5.3 Update monitor page to use design tokens
- [ ] 5.4 Update kanban page to use design tokens
- [ ] 5.5 Update lab page to use design tokens
- [ ] 5.6 Update arbitrage page to use design tokens
- [ ] 5.7 Update combo select page to use design tokens
- [ ] 5.8 Update external balances page to use design tokens

## 6. Testing

- [ ] 6.1 Test navigation on all 8 pages (desktop)
- [ ] 6.2 Test hamburger menu on all 8 pages (mobile)
- [ ] 6.3 Test responsive behavior at 375px, 768px, 1024px, 1440px widths
- [ ] 6.4 Verify no duplicate headers on any page
- [ ] 6.5 Take screenshots for QA evidence
