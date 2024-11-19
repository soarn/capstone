// Import Node.js modules installed via npm
import $ from 'jquery'; // jQuery
import * as bootstrap from 'bootstrap';     // Bootstrap
import gsap from 'gsap'; // GSAP
import { DateTime } from 'luxon'; //Luxon
import { computePosition } from '@floating-ui/dom'; // Floating UI (DOM)

// Import CSS Files


// DARK MODE TOGGLE
const themeToggle = document.getElementById("themeToggle");
const themeIcon = document.getElementById("themeIcon");

// Define dark-only themes
const darkThemes = ["darkly", "slate", "cyborg", "superhero", "quartz", "solar", "flatly"];

// Function to get the cookie value
function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
}

// Apply theme based on preference
function applyTheme(darkMode) {
  document.documentElement.setAttribute("data-bs-theme", darkMode ? "dark" : "light");
  themeIcon.setAttribute("data-feather", darkMode ? "sun" : "moon");
  document.getElementById("currentThemeName").textContent = darkMode ? "Light Mode" : "Dark Mode";
  feather.replace(); // Re-render feather icons after changing the icon
}

// Save theme to cookies and update theme when toggled
if (themeToggle) {
  themeToggle.addEventListener("click", function () {
    const darkMode = document.documentElement.getAttribute("data-bs-theme") !== "dark";
    document.cookie = `theme=${darkMode ? "dark" : "light"}; path=/; max-age=31536000`; // 1 year
    applyTheme(darkMode);
  });
}

// Set the initial theme based on cookies or user preference
document.addEventListener("DOMContentLoaded", function () {
  const isDarkMode = darkThemes.includes(userTheme) || getCookie("theme") === "dark";
  applyTheme(isDarkMode);

  // FLASH MESSAGES: Auto dismiss flash messages after 3 seconds
  setTimeout(function () {
    const alerts = document.querySelectorAll(".alert");
    alerts.forEach(function (alert) {
      alert.classList.add("fade");
      alert.classList.remove("show");
      setTimeout(() => alert.remove(), 1500);
    });
  }, 3000);

  // LOCALE AND TIME ZONE
  const userLocale = navigator.languages && navigator.languages.length
    ? navigator.languages[0]
    : navigator.language || navigator.userLanguage;

  const userTimeZone = Intl.DateTimeFormat().resolvedOptions().timeZone;

  document.cookie = `user_locale=${userLocale}; path=/; max-age=31536000`; // 1 year
  document.cookie = `user_time_zone=${userTimeZone}; path=/; max-age=31536000`; // 1 year
});

// Feather icons replacement
feather.replace();
