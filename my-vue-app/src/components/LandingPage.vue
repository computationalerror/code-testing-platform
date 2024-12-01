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
            <li @click="showChangePasswordForm = true">Change Password</li>
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
        <div class="rectangle-4" @click="goToTopicPage"></div>

        <div class="rectangle-5">
          <h2>Suggested Topics</h2>
          <div class="topics-grid">
    <div v-for="topic in suggestedTopics" :key="topic" class="topic-item">
      {{ topic }}
    </div>
  </div>
  <button @click="generateRandomTopics">Refresh</button>
</div>
      </div>
    </div>
  </div>
</template>

<script>
import userImage from '@/assets/user1.png';
import axios from '@/axios';
import { useRouter } from 'vue-router'; 

export default {
  name: "LandingPage",
  setup() {
    const router = useRouter();
    return { router };
  },
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
      allTopics: [
        // Basic Data Structures
        "Arrays", "Strings", "Linked Lists", "Stacks", "Queues",
        // Advanced Data Structures
        "Trees", "Binary Search Trees", "Heaps and Priority Queues", "Tries",
        "Disjoint Set Union (DSU)", "Fenwick Tree (Binary Indexed Tree)", 
        "Segment Tree", "Sparse Table",
        // Graph Algorithms
        "Graphs", "Breadth-First Search (BFS)", "Depth-First Search (DFS)",
        "Shortest Path Algorithms (Dijkstra, Bellman-Ford)",
        // Problem-Solving Techniques
        "Sliding Window", "Two Pointers", "Divide and Conquer", 
        "Backtracking", "Greedy Algorithms", "Recursion",
        // Sorting and Searching
        "Sorting Algorithms", "Searching Algorithms",
        // Mathematics and Number Theory
        "Bit Manipulation", "Modular Arithmetic", "Combinatorics", 
        "Number Theory",
        // Dynamic Programming (DP)
        "0/1 Knapsack", "Unbounded Knapsack", "Longest Increasing Subsequence (LIS)",
        "Longest Common Subsequence (LCS)", "Matrix Chain Multiplication",
        "Coin Change", "Subset Sum", "Partition Problem", "Minimum Path Sum",
        "Edit Distance", "Rod Cutting", "Palindromic Substrings", 
        "Egg Dropping Problem", "Fibonacci Variants", "Catalan Numbers",
        "Shortest Common Supersequence", "DP on Trees", "DP on Graphs", 
        "State Compression DP", "Bitmasking DP", "Interval DP", 
        "Digit DP", "Probability DP",
        // Game Theory and Miscellaneous
        "Matrix Manipulation", "Game Theory",
      ],
      suggestedTopics: [],
    };
  },
  mounted() {
    console.log('Initial preferences:', this.preferences);
    this.fetchPreferences();
    this.generateRandomTopics();
  },
  methods: {
    toggleDropdown() {
      this.showDropdown = !this.showDropdown;
    },
    selectOption(option) {
      console.log(option + " selected");
      if (option === 'Logout') {
        this.handleLogout();
      }
      this.showDropdown = false;
    },
    togglePreferencesDropdown() {
      this.showPreferences = !this.showPreferences;
    },
    async fetchPreferences() {
      console.log('Fetching preferences for email:', this.userEmail);
      if (!this.userEmail) {
        console.error('User  email not found in localStorage');
        return;
      }
      try {
        const response = await axios.get(`/get_preferences?email=${this.userEmail}`);
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
        const response = await axios.post('/update_preference', {
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
    async handleLogout() {
      try {
        // Call backend logout endpoint if needed
        await axios.post('/logout');
        
        // Clear all relevant items from localStorage
        localStorage.removeItem('userEmail');
        localStorage.removeItem('preferredLanguage');
        localStorage.removeItem('experienceLevel');
        localStorage.removeItem('token'); // If you're using authentication tokens
        
        // Close the dropdown
        this.showDropdown = false;
        
        // Redirect to home page
        this.router.push('/');
      } catch (error) {
        console.error('Error during logout:', error);
        // Even if the backend call fails, we should still clear local storage and redirect
        localStorage.clear();
        this.router.push('/');
      }
    },
    generateRandomTopics() {
      // Shuffle and select 4 topics
      const shuffled = [...this.allTopics].sort(() => 0.5 - Math.random());
      this.suggestedTopics = shuffled.slice(0, 4);
    },
    goToTopicPage() {
      this.$router.push('/topicpage');
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
  background-image: url("@/assets/bg.png");
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
  width: 95%;
  height: auto;
  padding: 20px;
  border-radius: 20px;
  text-align: center;
}

.rectangle-5 h2 {
  font-size: 1.8rem;
  color: #ffffff;
  margin-bottom: 15px;
}

.topics-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr); /* Two columns */
  gap: 15px; /* Space between items */
  justify-content: center;
}

.topic-item {
  font-size: 1.2rem;
  color: #004d40;
  padding: 10px;
  background-color: #c6f7cc;
  border-radius: 10px;
  box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.1);
}

.rectangle-5 button {
  font-size: 1rem;
  margin-top: 15px;
  padding: 10px 20px;
  color: white;
  border: none;
  border-radius: 5px;
  background-color: rgb(94, 135, 95);
  cursor: pointer;
}

.rectangle-5 button:hover {
  background-color: rgb(133, 206, 133);
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

.dropdown li , .preferences-dropdown li {
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