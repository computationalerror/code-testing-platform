<template>
    <div class="question-container">
      <h1>Questions on {{ decodedTopic }}</h1>
      
      <!-- Loading State -->
      <div v-if="loading" class="loading">
        <p>{{ loadingMessage }}</p>
        <div class="loading-spinner"></div>
      </div>
  
      <!-- Error State -->
      <div v-else-if="error" class="error">
        <p>{{ error }}</p>
        <button 
          @click="retryFetch" 
          class="retry-button" 
          :disabled="retryInProgress"
        >
          {{ retryInProgress ? `Retrying (${remainingRetries} attempts left)...` : 'Retry' }}
        </button>
      </div>
  
  
       <!-- Questions List -->
    <ul v-else-if="questions.length" class="questions-list">
      <li v-for="(question, index) in questions" :key="index">
        {{ question }}
      </li>
    </ul>

    <!-- No Questions State -->
    <div v-else-if="!loading && !error" class="no-questions">
      <p>No questions generated. Try a different topic or difficulty level.</p>
    </div>
  </div>
</template>
  <script>
  import axios from 'axios';
  
  const FLASK_API_URL = process.env.VUE_APP_FLASK_API_URL || 'http://127.0.0.1:5000';
  const MAX_RETRIES = 3;
  const INITIAL_RETRY_DELAY = 1000;
  const REQUEST_TIMEOUT = 200000; // 30 seconds timeout
  
  export default {
    name: 'QuestionComponent',
  
    data() {
    return {
      questions: [],
      loading: true,
      loadingMessage: 'Generating questions...',
      error: null,
      decodedTopic: '',
      userDifficulty: 'basic',
      retryCount: 0,
      remainingRetries: MAX_RETRIES,
      cancelTokenSource: null,
      retryInProgress: false
    };
  },
  
  created() {
    this.decodedTopic = decodeURIComponent(this.$route.params.topic || '');
    this.loadPreferences();
    this.cancelTokenSource = axios.CancelToken.source();
  },
  
  async mounted() {
    try {
      await this.fetchQuestions();
    } catch (error) {
      this.handleError(error);
    }
  },
  
    beforeUnmount() {
      this.cleanup();
    },
  
    methods: {
    cleanup() {
      if (this.cancelTokenSource) {
        this.cancelTokenSource.cancel('Component unmounted');
      }
    },
  
    loadPreferences() {
      try {
        const savedDifficulty = localStorage.getItem('experienceLevel');
        if (savedDifficulty) {
          this.userDifficulty = savedDifficulty;
        }
      } catch (error) {
        console.warn('Failed to load preferences:', error);
      }
    },
  
    savePreferences() {
      try {
        localStorage.setItem('experienceLevel', this.userDifficulty);
      } catch (error) {
        console.warn('Failed to save preferences:', error);
      }
    },
  
    async fetchQuestions() {
      this.loading = true;
      this.error = null;
      this.retryInProgress = false;

      for (this.retryCount = 0; this.retryCount < MAX_RETRIES; this.retryCount++) {
        try {
          const response = await axios.post(
            `${FLASK_API_URL}/generate-questions`,
            {
              topic: this.decodedTopic,
              difficulty: this.userDifficulty
            },
            {
              timeout: REQUEST_TIMEOUT,
              cancelToken: this.cancelTokenSource.token,
              headers: {
                'Content-Type': 'application/json'
              }
            }
          );

          // Check for valid response structure
          if (response.data?.questions && Array.isArray(response.data.questions)) {
            this.questions = response.data.questions.filter(q => q && typeof q === 'string');
            this.loading = false;
            return;
          }
          
          throw new Error('Invalid response format from server');
          
        } catch (error) {
          if (axios.isCancel(error)) {
            return;
          }

          this.remainingRetries = MAX_RETRIES - this.retryCount - 1;
          
          if (this.retryCount < MAX_RETRIES - 1) {
            this.retryInProgress = true;
            await new Promise(resolve => setTimeout(resolve, 
              INITIAL_RETRY_DELAY * Math.pow(2, this.retryCount))); // Exponential backoff
          } else {
            let errorMessage = 'Failed to generate questions';
            
            if (error.response) {
              // Server responded with error
              errorMessage = error.response.data?.error || 'Server error occurred';
            } else if (error.request) {
              // Request made but no response
              errorMessage = 'Server is not responding';
            } else {
              // Request setup error
              errorMessage = error.message || 'Failed to send request';
            }
            
            this.handleError(error, errorMessage);
          }
        }
      }
    },
  
    handleError(error, message = 'An error occurred') {
      this.error = message;
      this.loading = false;
      this.retryInProgress = false;
      console.error('Error details:', error);
    },
  
    async retryFetch() {
      this.retryCount = 0;
      this.remainingRetries = MAX_RETRIES;
      this.error = null;
      await this.fetchQuestions();
    }
  }
};
</script>
  
  <style>
  :root {
    --spacing: 20px;
    --border-radius: 4px;
    --transition-speed: 0.2s;
    --info-color: #2196F3;
    --border-color: #ccc;
    --background-light: #f5f5f5;
    --error-background: #ffebee;
    --danger-color: #f44336;
  }
  
  .question-container {
    padding: var(--spacing);
    max-width: 1200px;
    margin: 0 auto;
  }
  
  .error {
    color: var(--danger-color);
    padding: 15px;
    margin: 10px 0;
    border: 1px solid var(--danger-color);
    border-radius: var(--border-radius);
    background-color: var(--error-background);
    display: flex;
    flex-direction: column;
    gap: 10px;
    align-items: center;
    text-align: center;
  }
  
  .loading {
    text-align: center;
    padding: var(--spacing);
  }

  .no-questions {
  text-align: center;
  padding: 20px;
  background-color: var(--background-light);
  border-radius: var(--border-radius);
  margin-top: var(--spacing);
    }

    .loading-message {
  color: var(--info-color);
  font-style: italic;
    }
  
  .loading-spinner {
    border: 3px solid #f3f3f3;
    border-top: 3px solid var(--info-color);
    border-radius: 50%;
    width: 30px;
    height: 30px;
    animation: spin 1s linear infinite;
    margin: 10px auto;
  }
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
  
  .questions-list {
    list-style-type: none;
    padding: 0;
  }
  
  .questions-list li {
    padding: 10px;
    margin: 5px 0;
    background-color: #f8f9fa;
    border-radius: var(--border-radius);
    border: 1px solid #e9ecef;
    transition: transform var(--transition-speed);
  }
  
  .questions-list li:hover {
    transform: translateX(5px);
  }
  
  .retry-button {
    padding: 10px 20px;
    border: none;
    border-radius: var(--border-radius);
    cursor: pointer;
    font-weight: 500;
    transition: background-color var(--transition-speed);
    background-color: var(--info-color);
    color: white;
  }
  
  .retry-button:hover:not(:disabled) {
    filter: brightness(1.1);
  }
  
  .retry-button:disabled {
    background-color: #cccccc;
    cursor: not-allowed;
  }
  
  @media (max-width: 768px) {
    .question-container {
      padding: calc(var(--spacing) / 2);
    }
  }
  </style>