<template>
  <div class="home">
    <div class="content">
      <h1>{{ message }}</h1>
      <div class="links">
        <router-link to="/LoginPage" class="btn">Login</router-link>
        <router-link to="/RegisterPage" class="btn">Register</router-link>
      </div>
    </div>
  </div>
</template>

<script>
import axios from '@/axios';

export default {
  name: 'HomePage',
  data() {
    return {
      message: 'Loading...',  // Default message while data is being fetched
    };
  },
  async created() {
    try {
      // Fetch the welcome message from the Flask backend
      const response = await axios.get('/HomePage');
      this.message = response.data.message;  // Update the message with the data from Flask
    } catch (error) {
      console.error('Error fetching data:', error);
      this.message = 'Failed to load data';  // Update message on error
    }
  },
};
</script>

<style scoped>
.home {
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  padding: 20px;
  /* background: linear-gradient(90deg, #3d6244 0%, #e7e6ca 100%);  Fallback if image doesn't load */
  font-family: Arial, sans-serif;
}

.home::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: url('@/assets/dCKhFWzHyfwhoxntrgf7--3--v72ql.jpg');  
  background-size: cover;
  background-position: center;
  opacity: 0.6;  
  z-index: -1;  
}

.content {
  text-align: center;
  padding: 4rem;
  background-color: rgba(210, 239, 191, 0.607);
  border-radius: 25px;
  backdrop-filter: blur(10px);
  box-shadow: 0 8px 32px 0 rgba(24, 72, 44, 0.37);
  width: 80%;
  max-width: 600px;
}

h1 {
  font-size: 3.5rem;
  margin-bottom: 3rem;
  color: #072e0b;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.129);
}

.links {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2rem;
}

.btn {
  display: inline-block;
  padding: 1rem 2rem;
  font-size: 1.2rem;
  background-color: #315b35;
  color: white;
  text-decoration: none;
  border-radius: 30px;
  transition: all 0.3s ease;
  backdrop-filter: blur(5px);
  width: 60%;
  max-width: 300px;
}

.btn:hover {
  background-color: #072e0b;
  transform: translateY(-3px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}
</style>