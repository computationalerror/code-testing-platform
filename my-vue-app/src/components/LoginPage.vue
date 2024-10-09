<template>   
  <div class="login">     
    <h1>Login Page</h1>     
    <form @submit.prevent="handleLogin">       
      <div>         <label for="email">Email:</label>         
      <input type="email" v-model="email" required />       
      </div>       
      <div>         
        <label for="password">Password:</label>         
        <input type="password" v-model="password" required />       
        </div>       <button type="submit">Login</button>     
        </form>     
        <div class="links">       
          <router-link to="/RegisterPage">Don't have an account? Register</router-link>       
          <router-link to="/ForgotPassword">Forgot Password?</router-link>     
          </div>   
          </div> 
          </template>  
          <script> 
          import axios from '@/axios';  
          // Adjust the import based on your axios setup  
          export default 
          {   
            name: 'LoginPage',   data() 
            {     
              return {       
                email: '',       
                password: '',     
              };   
            },   
            methods: 
            {     
              async handleLogin() 
              {       
                try 
                {         
                  const response = await axios.post('http://127.0.0.1:5000/LoginPage', 
                  {           
                    email: this.email,           
                    password: this.password,         
                  });          
                  if (response.status === 200) 
                  {           
                    alert('Login successful!');           
                    localStorage.setItem('userEmail', this.email); 
                    // Store email for later use           
                    this.$router.push('/PreferencePage'); 
                    // Update with the route you want after login         
                    } else {           
                      alert(response.data.message || 'Login failed!');         
                      }       
                      } catch (error) 
                      {         
                        console.error('Login error:', error);         
                        alert('An error occurred during login.');       
                        }     
                        },   
                        }, 
                        }; 
                        </script>  
                        <style scoped> 
                        .login {   
                          display: flex;   
                          flex-direction: column;  
                          align-items: center;   
                          justify-content: center;   
                          height: 100vh;   
                          background: linear-gradient(135deg, #3d6244 0%, #e7e6ca 100%);   
                          color: white;   
                          font-family: Arial, sans-serif;   
                          background-image: url("@/assets/bg.png");   
                          background-size: cover;    
                          background-position: center;   
                          background-repeat: no-repeat; 
                          }  
                          h1 
                          {   
                          font-size: 2.5rem;  
                          margin-bottom: 2rem;   
                          color: #072e0b;   
                          text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.129); 
                          }  
                          form 
                          {   
                          background-color: rgba(210, 239, 191, 0.607);   
                          padding: 2rem;   
                          border-radius: 25px;   
                          backdrop-filter: blur(10px);   
                          box-shadow: 0 8px 32px 0 rgba(24, 72, 44, 0.37);   
                          width: 300px;   
                          display: flex;   
                          flex-direction: column;   
                          align-items: center; 
                          }  
                          form div 
                          {   
                          margin-bottom: 1rem;   width: 100%; 
                          }  
                          label {   display: block;   margin-bottom: 0.5rem;   color: #072e0b; }  
                          input {   width: 100%;   padding: 0.5rem;   border: none;   border-radius: 5px;   background-color: rgba(255, 255, 255, 0.2);   color: rgb(0, 0, 0);   outline: none; }  
                          button {   width: 100%;   padding: 0.8rem;   background-color: #315b35;   color: white;   border: none;   border-radius: 30px;   cursor: pointer;   transition: background-color 0.3s ease; }  
                          button:hover {   background-color: #072e0b; }  
                          .links {   margin-top: 1rem;   display: flex;   flex-direction: column;   align-items: center; }  
                          .links a {   color: #072e0b;   text-decoration: none;   margin: 0.5rem 0;   transition: color 0.3s ease; }  
                          .links a:hover {   color: #315b35; } 
                          </style>