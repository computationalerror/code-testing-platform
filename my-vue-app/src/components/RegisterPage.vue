<template>
  <div class="register">
    <h1>Register Page</h1>
    <form @submit.prevent="handleRegister">
      <div>
        <label for="fullName">Full Name:</label>
        <input type="text" v-model="fullName" required />
      </div>
      <div>
        <label for="email">Email:</label>
        <input type="email" v-model="email" required />
      </div>
      <div>
        <label for="password">Password:</label>
        <input type="password" v-model="password" required />
      </div>
      <div>
        <label for="repeatPassword">Repeat Password:</label>
        <input type="password" v-model="repeatPassword" required />
      </div>
      <button type="submit">Register</button>
    </form>
    <router-link to="/LoginPage">Already have an account? Login</router-link>
  </div>
</template>

<script>
import axios from '@/axios';

export default {
  name: 'RegisterPage',
  data() {
    return {
      fullName: '',
      email: '',
      password: '',
      repeatPassword: '',
    };
  },
  methods: {
    async handleRegister() {
      // Check if passwords match
      if (this.password !== this.repeatPassword) {
        alert('Passwords do not match!');
        return;
      }

      try {
        // Send registration request to backend
        const response = await axios.post('/RegisterPage', {
          full_name: this.fullName,
          email: this.email,
          password: this.password,
        });

        if (response.status === 201) {
          // Save the user's email to localStorage
          localStorage.setItem('userEmail', this.email);

          // Show success message
          alert('Registration successful!');

          // Redirect to login page
          this.$router.push('/LoginPage');
        } else {
          alert(response.data.message || 'Registration failed!');
        }
      } catch (error) {
        console.error('Registration error:', error);
        alert('An error occurred during registration.');
      }
    },
  },
};
</script>

<style scoped>
.register {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
  color: rgb(0, 0, 0);
  font-family: Arial, sans-serif;
  background-image: url("@/assets/bg.png");
  background-size: cover; 
  background-position: center;
  background-repeat: no-repeat;
}

h1 {
  font-size: 2.5rem;
  margin-bottom: 2rem;
  color: #072e0b;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.129);
}

form {
  background-color: rgba(210, 239, 191, 0.607);
  padding: 2rem;
  border-radius: 25px;
  backdrop-filter: blur(10px);
  box-shadow: 0 8px 32px 0 rgba(24, 72, 44, 0.37);
  width: 300px;
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 1rem;
}

form div {
  margin-bottom: 1rem;
  width: 100%;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  color: #072e0b;
}

input {
  width: 100%;
  padding: 0.5rem;
  border: none;
  border-radius: 5px;
  background-color: rgba(255, 255, 255, 0.2);
  color: rgb(6, 28, 8);
  outline: none;
}

input:focus {
  outline: 2px solid rgb(94, 135, 95);
}

button {
  width: 100%;
  padding: 0.8rem;
  background-color: #315b35;
  color: white;
  border: none;
  border-radius: 30px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

button:hover {
  background-color: #072e0b;
}

.router-link {
  color: #072e0b;
  text-decoration: none;
  transition: color 0.3s ease;
}

.router-link:hover {
  color: #315b35;
}
</style>