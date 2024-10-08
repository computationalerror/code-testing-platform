<template>
  <div class="desktop">
    <!-- Taskbar at the top -->
    <div class="taskbar">
      <!-- Profile icon in the taskbar -->
      <div class="user-profile">
        <img
          :src="userImage"
          alt="User"
          class="profile-icon"
          @click="toggleDropdown"
        />
        <!-- Dropdown with dummy options -->
        <div v-if="showDropdown" class="dropdown">
          <ul>
            <li @click="selectOption('Profile Update')">Profile Update</li>
            <li @click="selectOption('Change Password')">Change Password</li>
            <li @click="selectOption('Settings')">Settings</li>
            <li @click="selectOption('Help')">Help</li>
            <li @click="selectOption('Logout')">Logout</li>
          </ul>
        </div>
      </div>
    </div>

    <div class="content">
      <!-- Left panel -->
      <div class="left-panel">
        <div class="rectangle-1" @click="togglePreferencesDropdown">
          Preferences
        </div>
        <div v-if="showPreferences" class="preferences-dropdown">
          <h3>Language</h3>
          <ul>
            <li 
              v-for="lang in languages" 
              :key="lang"
              @click="updatePreference('preferredLanguage', lang)"
              :class="{ 'selected': preferences.preferredLanguage === lang }"
            >
              {{ lang }}
            </li>
          </ul>
          <h3>Experience Level</h3>
          <ul>
            <li 
              v-for="level in experienceLevels" 
              :key="level"
              @click="updatePreference('experienceLevel', level)"
              :class="{ 'selected': preferences.experienceLevel === level }"
            >
              {{ level }}
            </li>
          </ul>
        </div>
        <div class="rectangle-2"></div>
        <div class="rectangle-3"></div>
      </div>      

      <!-- Right panel -->
      <div class="right-panel">
        <div class="rectangle-4"></div>
        <div class="rectangle-5"></div>
      </div>
    </div>
  </div>
</template>

<script>
import userImage from '@/assets/user1.png';
import axios from '@/axios';

export default {
  name: "LandingPage",
  data() {
    return {
      showDropdown: false,
      showPreferences: false,
      preferences: {
        preferredLanguage: localStorage.getItem('preferredLanguage') || '',
        experienceLevel: localStorage.getItem('experienceLevel') || ''
      },
      languages: ['Java', 'Python', 'C++'],
      experienceLevels: ['Beginner', 'Intermediate', 'Expert'],
      userImage,
      userEmail: localStorage.getItem('userEmail') || '',
    };
  },
  mounted() {
    console.log('Initial preferences:', this.preferences);
    this.fetchPreferences();
  },
  methods: {
    toggleDropdown() {
      this.showDropdown = !this.showDropdown;
    },
    selectOption(option) {
      console.log(option + " selected");
      this.showDropdown = false;
    },
    togglePreferencesDropdown() {
      this.showPreferences = !this.showPreferences;
    },
    async fetchPreferences() {
      console.log('Fetching preferences for email:', this.userEmail);
      if (!this.userEmail) {
        console.error('User email not found in localStorage');
        return;
      }
      try {
        const response = await axios.get(`http://127.0.0.1:5000/get_preferences?email=${this.userEmail}`);
        console.log('Fetched preferences:', response.data);
        if (response.data && response.data.length > 0) {
          const fetchedPreferences = response.data[0];
          this.preferences.preferredLanguage = fetchedPreferences.preferred_language || this.preferences.preferredLanguage;
          this.preferences.experienceLevel = fetchedPreferences.experience_level || this.preferences.experienceLevel;
          
          // Update localStorage
          localStorage.setItem('preferredLanguage', this.preferences.preferredLanguage);
          localStorage.setItem('experienceLevel', this.preferences.experienceLevel);
          
          console.log('Updated preferences:', this.preferences);
        }
      } catch (error) {
        console.error('Error fetching preferences:', error);
      }
    },
    async updatePreference(key, value) {
      console.log(`Updating preference: ${key} = ${value}`);
      if (!this.userEmail) {
        console.error('User email not found');
        return;
      }
      try {
        const response = await axios.post('http://127.0.0.1:5000/update_preference', {
          email: this.userEmail,
          [key]: value
        });
        console.log('Preference updated:', response.data);
        this.preferences[key] = value;
        
        // Update localStorage
        localStorage.setItem(key, value);
        
        console.log('Updated preferences:', this.preferences);
      } catch (error) {
        console.error('Error updating preference:', error);
      }
    },
  },
};
</script>

<style scoped>
.desktop {
  background-color: #efefef;
  display: flex;
  flex-direction: column;
  width: 100vw;
  height: 100vh;
  overflow: auto;
  background-image: url("C:/Users/Asus/OneDrive/Documents/GitHub/code-testing-platform/test_platform/my-vue-app/src/assets/bg.png");
  background-size: cover; 
  background-position: center;
  background-repeat: no-repeat;
  background-attachment: fixed;
}

.taskbar {
  background-color: #072e0b;
  height: 50px;
  width: 100%;
  position: fixed;
  top: 0;
  left: 0;
  display: flex;
  justify-content: flex-end;
  align-items: center;
  padding-right: 20px;
  z-index: 10;
}

.content {
  display: flex;
  justify-content: space-between;
  width: 100%;
  margin-top: 50px;
  padding: 30px;
  box-sizing: border-box;
  min-height: calc(100vh - 50px);
}

.left-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
  width: 48%;
  position: relative;
}

.right-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
  width: 48%;
}

.rectangle-1, .rectangle-2, .rectangle-3, .rectangle-4, .rectangle-5 {
  background-color: #315b35;
  border-radius: 20px;
  background-size: contain;
  background-position: center;
  background-repeat: no-repeat;
}

.rectangle-1 {
  width: 240px;
  height: 68px;
  border-radius: 10px;
  color: white;
  font-size: 1.2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.rectangle-2 {
  width: 720px;
  height: 340px;
  background-image: url("@/assets/streak.png");
}

.rectangle-3 {
  width: 720px;
  height: 473px;
  background-image: url("@/assets/report.png");
}

.rectangle-4 {
  width: 100%;
  height: 418px;
  background-image: url("@/assets/2.png");
}

.rectangle-5 {
  width: 100%;
  height: 418px;
  background-image: url("@/assets/1.png");
}

.user-profile {
  position: relative;
}

.profile-icon {
  cursor: pointer;
  border-radius: 50%;
  width: 30px;
  height: 30px;
  margin-right: 70px;
}

.dropdown, .preferences-dropdown {
  position: absolute;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  z-index: 100;
}

.dropdown {
  right: 0;
  top: 40px;
  width: 180px;
}

.preferences-dropdown {
  top: 80px;
  left: 0;
  width: 200px;
  padding: 15px;
  background-color: #f9f9f9;
  border: 1px solid #ddd;
}

.dropdown ul, .preferences-dropdown ul {
  list-style: none;
  margin: 0;
  padding: 0;
}

.dropdown li, .preferences-dropdown li {
  padding: 10px;
  cursor: pointer;
  color: #072e0b;
}

.dropdown li:hover, .preferences-dropdown li:hover {
  background-color: #f0f0f0;
}

.preferences-dropdown h3 {
  margin-top: 10px;
  margin-bottom: 5px;
  color: #072e0b;
  font-size: 1rem;
}

.preferences-dropdown li {
  padding: 8px 12px;
  margin: 2px 0;
  border-radius: 4px;
  transition: all 0.3s ease;
}

.preferences-dropdown li.selected {
  background-color: #072e0b;
  color: white;
}

@media (max-width: 1400px) {
  .content {
    flex-direction: column;
    align-items: center;
  }

  .left-panel, .right-panel {
    width: 100%;
    max-width: 720px;
  }

  .rectangle-2, .rectangle-3, .rectangle-4, .rectangle-5 {
    width: 100%;
  }
}

@media (max-width: 768px) {
  .rectangle-1, .rectangle-2, .rectangle-3, .rectangle-4, .rectangle-5 {
    width: 100%;
    height: 0;
    padding-bottom: 56.25%; /* 16:9 Aspect Ratio */
    position: relative;
  }

  .rectangle-1 {
    padding-bottom: 28.33%; /* Approximately 68/240 */
  }

  .preferences-dropdown {
    width: 100%;
    top: 100%;
    left: 0;
  }
}
</style>