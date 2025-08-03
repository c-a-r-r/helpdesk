<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script setup>
// App.vue now just renders the router view
// Authentication logic is handled in LoginView component
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

#app {
  min-height: 100vh;
}

/* Hide Vue DevTools overlay */
iframe[src*="devtools"] {
  display: none !important;
}

.__vue-devtools-iframe__ {
  display: none !important;
}
</style>