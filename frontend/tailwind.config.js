/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                // "Industrial" Palette - Carbon & Safety Orange
                primary: {
                    DEFAULT: '#ff5500', // Safety Orange
                    50: '#fff7ed',
                    100: '#ffedd5',
                    200: '#fed7aa',
                    300: '#fdba74',
                    400: '#fb923c',
                    500: '#f97316',
                    600: '#ff5500', // Main Safety Orange
                    700: '#c2410c',
                    800: '#9a3412',
                    900: '#111111', // Deep Carbon
                    950: '#0a0a0a', // Almost Black
                },
                industrial: {
                    50: '#f9f9f9',
                    100: '#f0f0f0',
                    200: '#e0e0e0',
                    300: '#cccccc',
                    400: '#a3a3a3',
                    500: '#737373',
                    600: '#525252',
                    700: '#404040',
                    800: '#262626',
                    900: '#171717', // Structural Heavy Grey
                }
            },
            animation: {
                'scan': 'scan 4s linear infinite',
            },
            keyframes: {
                scan: {
                    '0%': { backgroundPosition: '0% 50%' },
                    '100%': { backgroundPosition: '100% 50%' },
                },
            },
            boxShadow: {
                'hard': '4px 4px 0px 0px rgba(255, 85, 0, 0.4)', // Hard shadow, zero blur
                'hard-sm': '2px 2px 0px 0px rgba(255, 85, 0, 0.4)',
            },
        },
    },
    plugins: [],
}
