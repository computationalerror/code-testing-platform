<template>
  <div class="ide-container">
    <h1>Questions on {{ decodedTopic }}</h1>
    <div v-if="loading" class="loading">
      <p>{{ loadingMessage }}</p>
      <div class="loading-spinner"></div>
    </div>
    <div v-else-if="error" class="error">
      <p>{{ error }}</p>
      <button @click="retryFetch" class="retry-button" :disabled="retryInProgress">
        {{ retryInProgress ? Retrying (${remainingRetries} attempts left)... : 'Retry' }}
      </button>
    </div>
    <ul v-else-if="questions.length" class="questions-list">
      <li v-for="(question, index) in questions" :key="index">
        {{ question }}
      </li>
    </ul>
    
    <div class="controls">
      <select 
        v-model="selectedLanguage" 
        class="language-select"
        :disabled="loading"
      >
        <option value="javascript">JavaScript</option>
        <option value="python">Python</option>
        <option value="cpp">C++</option>
        <option value="java">Java</option>
      </select>
    </div>

    <div id="editor" ref="editor"></div>

    <div class="button-container">
      <button 
        @click="runCode" 
        :disabled="loading || !editor || isRunning" 
        class="run-button"
      >
        {{ isRunning ? 'Running...' : 'Run Code' }}
      </button>
      <button 
        @click="resetEditor" 
        :disabled="loading || !editor" 
        class="reset-button"
      >
        Reset Code
      </button>
    </div>

    <div v-if="output !== null" class="output-container">
      <h3>Output:</h3>
      <pre>{{ output }}</pre>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import * as monaco from 'monaco-editor';

const API_BASE_URL = process.env.VUE_APP_API_BASE_URL || 'http://127.0.0.1:5000';
const MAX_RETRIES = 3;
const INITIAL_RETRY_DELAY = 1000;
const MAX_RETRY_DELAY = 5000;
const REQUEST_TIMEOUT = 10000;

export default {
  name: 'IDEComponent',
  
  data() {
    return {
      editor: null,
      selectedLanguage: 'javascript',
      output: null,
      questions: [],
      loading: true,
      loadingMessage: 'Loading questions...',
      error: null,
      decodedTopic: '',
      userDifficulty: 'basic',
      isRunning: false,
      retryCount: 0,
      retryInProgress: false,
      remainingRetries: MAX_RETRIES,
      cancelTokenSource: null,
      defaultCode: {
        javascript: '// Write your JavaScript code here\n\n',
        python: '# Write your Python code here\n\n',
        cpp: '// Write your C++ code here\n\n',
        java: '// Write your Java code here\n\n'
      }
    };
  },

  created() {
    this.decodedTopic = decodeURIComponent(this.$route.params.topic || '');
    this.loadPreferences();
    this.cancelTokenSource = axios.CancelToken.source();
  },

  async mounted() {
    try {
      await this.initializeEditor();
      await this.fetchQuestions();
    } catch (error) {
      this.handleError(error, 'Failed to initialize the IDE');
    }
  },

  beforeUnmount() {
    this.cleanup();
  },

  watch: {
    selectedLanguage(newLanguage) {
      if (this.editor) {
        monaco.editor.setModelLanguage(this.editor.getModel(), newLanguage);
        // Fixed: Use Object.prototype.hasOwnProperty.call instead of direct method access
        this.editor.setValue(Object.prototype.hasOwnProperty.call(this.defaultCode, newLanguage) 
          ? this.defaultCode[newLanguage] 
          : '');
        this.savePreferences();
      }
    }
  },

  methods: {
    cleanup() {
      if (this.editor) {
        this.editor.dispose();
      }
      if (this.cancelTokenSource) {
        this.cancelTokenSource.cancel('Component unmounted');
      }
    },

    loadPreferences() {
      try {
        const savedLanguage = localStorage.getItem('preferredLanguage');
        const savedDifficulty = localStorage.getItem('experienceLevel');
        
        if (savedLanguage && Object.prototype.hasOwnProperty.call(this.defaultCode, savedLanguage)) {
          this.selectedLanguage = savedLanguage;
        }
        
        if (savedDifficulty) {
          this.userDifficulty = savedDifficulty;
        }
      } catch (error) {
        console.warn('Failed to load preferences:', error);
      }
    },

    savePreferences() {
      try {
        localStorage.setItem('preferredLanguage', this.selectedLanguage);
        localStorage.setItem('experienceLevel', this.userDifficulty);
      } catch (error) {
        console.warn('Failed to save preferences:', error);
      }
    },

    async initializeEditor() {
      await this.$nextTick();
      
      try {
        this.editor = monaco.editor.create(this.$refs.editor, {
          value: this.defaultCode[this.selectedLanguage],
          language: this.selectedLanguage,
          theme: 'vs-dark',
          automaticLayout: true,
          minimap: { enabled: false },
          scrollBeyondLastLine: false,
          lineNumbers: 'on',
          roundedSelection: false,
          scrollbar: {
            vertical: 'visible',
            horizontal: 'visible'
          },
          fontSize: 14,
          tabSize: 2,
          wordWrap: 'on'
        });
        
        this.editor.onDidChangeModelContent(() => {
          try {
            const model = this.editor.getModel();
            if (model) {
              monaco.editor.setModelMarkers(model, 'owner', []);
            }
          } catch (error) {
            console.warn('Editor warning:', error);
          }
        });
      } catch (error) {
        throw new Error('Failed to initialize code editor: ' + error.message);
      }
    },

    calculateRetryDelay(retryCount) {
      const baseDelay = Math.min(
        INITIAL_RETRY_DELAY * Math.pow(2, retryCount),
        MAX_RETRY_DELAY
      );
      return baseDelay + Math.random() * 1000;
    },

    // Fixed: Removed unused parameter
    async fetchQuestionsWithTimeout() {
      if (this.cancelTokenSource) {
        this.cancelTokenSource.cancel('New request initiated');
      }
      this.cancelTokenSource = axios.CancelToken.source();

      try {
        const response = await axios.post(
          ${API_BASE_URL}/generate-questions,
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

        if (!response.data?.questions || !Array.isArray(response.data.questions)) {
          throw new Error('Invalid response format');
        }

        return response.data.questions;
      } catch (error) {
        if (axios.isCancel(error)) {
          throw new Error('Request cancelled');
        }
        
        if (error.code === 'ECONNABORTED') {
          throw new Error('Request timed out');
        }

        const status = error.response?.status;
        if (status === 500) {
          throw new Error('Server error occurred');
        }

        throw error;
      }
    },

    async fetchQuestions() {
      this.loading = true;
      this.error = null;
      this.retryInProgress = false;
      this.remainingRetries = MAX_RETRIES;
      this.retryCount = 0;

      while (this.retryCount < MAX_RETRIES) {
        try {
          this.questions = await this.fetchQuestionsWithTimeout();
          this.loading = false;
          return;
        } catch (error) {
          this.retryCount++;
          this.remainingRetries = MAX_RETRIES - this.retryCount;

          if (this.retryCount < MAX_RETRIES) {
            this.retryInProgress = true;
            this.loadingMessage = Attempt ${this.retryCount + 1} of ${MAX_RETRIES}...;
            await new Promise(resolve => 
              setTimeout(resolve, this.calculateRetryDelay(this.retryCount))
            );
          } else {
            this.handleError(error);
          }
        }
      }
    },

    handleError(error, defaultMessage = '') {
      let errorMessage = defaultMessage || 'An unexpected error occurred';
      
      if (error.message.includes('timeout')) {
        errorMessage = 'The request timed out. Please check your connection and try again.';
      } else if (error.message.includes('Network Error')) {
        errorMessage = 'Cannot connect to the server. Please check your internet connection.';
      } else if (error.response?.status === 500) {
        errorMessage = 'The server encountered an error. Please try again later.';
      }

      this.error = errorMessage;
      this.loading = false;
      this.retryInProgress = false;
      console.error('Error details:', error);
    },

    async retryFetch() {
      if (this.retryInProgress) return;
      this.retryCount = 0;
      this.error = null;
      await this.fetchQuestions();
    },

    async runCode() {
      if (!this.editor || this.isRunning) return;
      
      const code = this.editor.getValue();
      this.isRunning = true;
      this.output = null;
      
      try {
        const response = await axios.post(${API_BASE_URL}/execute-code, {
          code,
          language: this.selectedLanguage
        }, {
          timeout: REQUEST_TIMEOUT
        });
        
        this.output = response.data.output;
      } catch (error) {
        this.output = Error executing code: ${error.response?.data?.message || error.message};
      } finally {
        this.isRunning = false;
      }
    },

    resetEditor() {
      if (this.editor) {
        this.editor.setValue(this.defaultCode[this.selectedLanguage]);
        this.output = null;
        
        const model = this.editor.getModel();
        if (model) {
          monaco.editor.setModelMarkers(model, 'owner', []);
        }
      }
    }
  }
};
</script>

<style scoped>
.ide-container {
padding: 20px;
max-width: 1200px;
margin: 0 auto;
}

#editor {
height: 400px;
border: 1px solid #ccc;
margin: 20px 0;
border-radius: 4px;
}

.controls {
margin: 20px 0;
display: flex;
gap: 10px;
align-items: center;
}

.language-select {
padding: 8px 12px;
border-radius: 4px;
border: 1px solid #ccc;
background-color: white;
font-size: 14px;
}

.button-container {
display: flex;
gap: 10px;
margin: 20px 0;
}

.run-button, .reset-button, .retry-button {
padding: 10px 20px;
border: none;
border-radius: 4px;
cursor: pointer;
font-weight: 500;
transition: background-color 0.2s;
}

.run-button {
background-color: #4CAF50;
color: white;
}

.reset-button {
background-color: #f44336;
color: white;
}

.retry-button {
background-color: #2196F3;
color: white;
}

.run-button:disabled, .reset-button:disabled {
background-color: #cccccc;
cursor: not-allowed;
}

.error {
color: #f44336;
padding: 15px;
margin: 10px 0;
border: 1px solid #f44336;
border-radius: 4px;
background-color: #ffebee;
}

.output-container {
margin-top: 20px;
padding: 15px;
background-color: #f5f5f5;
border-radius: 4px;
border: 1px solid #e0e0e0;
}

.loading {
text-align: center;
padding: 20px;
}

.loading-spinner {
border: 3px solid #f3f3f3;
border-top: 3px solid #3498db;
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
border-radius: 4px;
border: 1px solid #e9ecef;
}

.error {
color: #f44336;
padding: 15px;
margin: 10px 0;
border: 1px solid #f44336;
border-radius: 4px;
background-color: #ffebee;
display: flex;
flex-direction: column;
gap: 10px;
align-items: center;
}

.retry-button:disabled {
background-color: #90caf9;
cursor: not-allowed;
}
</style>