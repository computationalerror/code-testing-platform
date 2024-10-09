<template>
  <div class="forgot-password">
    <h2>Forgot Password</h2>
    <form @submit.prevent="handleSubmit">
      <div v-if="step === 1">
        <label for="email">Email:</label>
        <input type="email" id="email" v-model="email" required />
        <button type="submit">Send Verification Code</button>
      </div>
      <div v-if="step === 2">
        <label for="verificationCode">Verification Code:</label>
        <input type="text" id="verificationCode" v-model="verificationCode" required />
        <button type="submit">Verify Code</button>
      </div>
      <div v-if="step === 3">
        <label for="newPassword">New Password:</label>
        <input type="password" id="newPassword" v-model="newPassword" required />
        <label for="confirmPassword">Confirm Password:</label>
        <input type="password" id="confirmPassword" v-model="confirmPassword" required />
        <button type="submit">Reset Password</button>
      </div>
    </form>
    <p v-if="message" :class="{ 'error-message': isError }">{{ message }}</p>
  </div>
</template>

<script>
import axios from '@/axios';

export default {
  name: 'ForgotPassword',
  data() {
    return {
      step: 1,
      email: '',
      verificationCode: '',
      newPassword: '',
      confirmPassword: '',
      message: '',
      isError: false,
    };
  },
  methods: {
    async handleSubmit() {
      try {
        if (this.step === 1) {
          await this.sendVerificationCode();
        } else if (this.step === 2) {
          await this.verifyCode();
        } else if (this.step === 3) {
          await this.resetPassword();
        }
      } catch (error) {
        console.error('Error:', error);
        this.showError('An error occurred. Please try again.');
      }
    },
    async sendVerificationCode() {
      const response = await axios.post('http://127.0.0.1:5000/send-verification-code', { email: this.email });
      if (response.data.success) {
        this.showMessage(response.data.message);
        this.step = 2;
      } else {
        this.showError(response.data.message);
      }
    },
    async verifyCode() {
      const response = await axios.post('http://127.0.0.1:5000/verify-code', { 
        email: this.email, 
        verificationCode: this.verificationCode 
      });
      if (response.data.success) {
        this.showMessage(response.data.message);
        this.step = 3;
      } else {
        this.showError(response.data.message);
      }
    },
    async resetPassword() {
      if (this.newPassword !== this.confirmPassword) {
        this.showError('Passwords do not match');
        return;
      }
      const response = await axios.post('http://127.0.0.1:5000/reset-password', {
        email: this.email,
        verificationCode: this.verificationCode,
        newPassword: this.newPassword
      });
      if (response.data.success) {
        this.showMessage(response.data.message);
        // Redirect to login page after successful password reset
        setTimeout(() => this.$router.push('/LoginPage'), 2000);
      } else {
        this.showError(response.data.message);
      }
    },
    showMessage(message) {
      this.message = message;
      this.isError = false;
    },
    showError(message) {
      this.message = message;
      this.isError = true;
    }
  }
};
</script>

<style scoped>
.forgot-password {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
  color: white;
  font-family: Arial, sans-serif;
  background-image: url("@/assets/bg.png");
  background-size: cover; 
  background-position: center;
  background-repeat: no-repeat;
}

h2 {
  font-size: 2rem;
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
  justify-content: center;
}

form div {
  margin-bottom: 1.5rem; /* Increased space between elements */
  width: 100%;
  align-items: center;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  color: #072e0b;
  align-items: center;
}

input {
  width: 100%;
  padding: 0.5rem;
  margin-bottom: 1rem; /* Add margin between input fields */
  border: none;
  border-radius: 5px;
  background-color: rgba(255, 255, 255, 0.2);
  color: rgb(0, 0, 0);
  outline: none;
  align-items: center;
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

.error-message {
  color: red;
}
</style>