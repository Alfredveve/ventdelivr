/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        "./templates/**/*.html", "./**/templates/**/*.html",
    ],
    theme: {
        extend: {
            colors: {
                'african-orange': '#FF4D00',
                'african-green': '#1B4332',
                'african-gold': '#FFB703'
            }
        }
    },
    plugins: []
}
