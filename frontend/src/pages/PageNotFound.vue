<template>
  <section class="not-found">
    <h1>404 – Page Not Found</h1>
    <p>The page you're looking for doesn't exist or was moved.</p>
    <RouterLink class="back-home" to="/">← Go back to homepage</RouterLink>
  </section>
</template>

<style scoped>
.not-found {
  display: flex;
  flex-direction: column;
  max-width: 600px;
  margin: auto;
  padding: 5rem 2rem;
  gap: 1.5rem;
  text-align: center;
}

h1 {
  color: #111;
  font-size: 2rem;
}

p {
  color: #444;
  font-size: 1.1rem;
}

.back-home {
  color: #007c8a;
  font-weight: bold;
  text-decoration: none;
}

.back-home:hover {
  text-decoration: underline;
}
</style>
