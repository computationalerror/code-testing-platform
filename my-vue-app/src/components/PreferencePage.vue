<template>
  <div class="setup-page">
    <h1>Setup Your Profile</h1>

    <div v-if="step === 1">
      <h2>Which language would you like to practice today?</h2>
      <div class="options">
        <button @click="selectLanguage('java')">Java</button>
        <button @click="selectLanguage('python')">Python</button>
        <button @click="selectLanguage('c++')">C++</button>
      </div>
    </div>

    <div v-if="step === 2">
      <h2>How would you describe your experience level?</h2>
      <div class="options">
        <button @click="selectExperience('beginner')">Beginner</button>
        <button @click="selectExperience('intermediate')">Intermediate</button>
        <button @click="selectExperience('expert')">Expert</button>
      </div>
    </div>

    <div v-if="step === 3">
      <h2>Let's get you started!</h2>
      <p>Preferred Language: {{ preferredLanguage }}</p>
      <p>Experience Level: {{ experienceLevel }}</p>
      <p>You can now proceed to your dashboard.</p>
    </div>
  </div>
</template>

<script>
import axios from '@/axios';

export default {
  name: 'SetupPage',
  data() {
    return {
      step: 1,
      preferredLanguage: '',
      experienceLevel: '',
      userEmail: localStorage.getItem('userEmail') || '',
    };
  },
  methods: {
    selectLanguage(language) {
      this.preferredLanguage = language;
      this.step = 2;
    },
    async selectExperience(level) {
      this.experienceLevel = level;
      this.step = 3;
      console.log('Setup complete', {
        experienceLevel: this.experienceLevel,
        preferredLanguage: this.preferredLanguage,
      });
      await this.savePreferences();
    },
    async savePreferences() {
      console.log('User email before saving preferences:', this.userEmail);
      try {
        const response = await axios.post('http://127.0.0.1:5000/save_preferences', {
          email: this.userEmail,
          preferredLanguage: this.preferredLanguage,
          experienceLevel: this.experienceLevel,
        });
        console.log('Preferences saved:', response.data);

        // Store preferences in localStorage
        localStorage.setItem('preferredLanguage', this.preferredLanguage);
        localStorage.setItem('experienceLevel', this.experienceLevel);

        this.$router.push({ name: 'LandingPage' });
      } catch (error) {
        console.error('Error saving preferences:', error);
      }
    },
  },
};
</script>

<style scoped>
.setup-page {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
  color: white;
  font-family: Arial, sans-serif;
  background-image: url("C:/Users/Asus/OneDrive/Documents/GitHub/code-testing-platform/test_platform/my-vue-app/src/assets/bg.png");
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

h2 {
  margin-top: 20px;
  color: #072e0b;
  font-size: 1.8rem;
}

.options {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 30px;
}

button {
  padding: 12px 24px;
  font-size: 16px;
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

p {
  font-size: 1.2rem;
  margin-top: 20px;
  color: #315b35;
}
</style>