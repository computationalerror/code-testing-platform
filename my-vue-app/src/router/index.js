import { createRouter, createWebHistory } from 'vue-router';
import HomePage from 'C:/Users/Asus/OneDrive/Documents/GitHub/code-testing-platform/test_platform/my-vue-app/src/components/HomePage.vue';
import LoginPage from 'C:/Users/Asus/OneDrive/Documents/GitHub/code-testing-platform/test_platform/my-vue-app/src/components/LoginPage.vue';
import RegisterPage from 'C:/Users/Asus/OneDrive/Documents/GitHub/code-testing-platform/test_platform/my-vue-app/src/components/RegisterPage.vue';
import ForgotPassword from 'C:/Users/Asus/OneDrive/Documents/GitHub/code-testing-platform/test_platform/my-vue-app/src/components/ForgotPassword.vue';
import PreferencePage from 'C:/Users/Asus/OneDrive/Documents/GitHub/code-testing-platform/test_platform/my-vue-app/src/components/PreferencePage.vue';
import LandingPage from 'C:/Users/Asus/OneDrive/Documents/GitHub/code-testing-platform/test_platform/my-vue-app/src/components/LandingPage.vue';

const routes = [{
        path: '/',
        name: 'HomePage',
        component: HomePage,
    },
    {
        path: '/LoginPage',
        name: 'LoginPage',
        component: LoginPage,
    },
    {
        path: '/RegisterPage',
        name: 'RegisterPage',
        component: RegisterPage,
    },
    {
        path: '/ForgotPassword',
        name: 'ForgotPassword',
        component: ForgotPassword,
    },
    {
        path: '/PreferencePage',
        name: 'PreferencePage',
        component: PreferencePage,
    },
    {
        path: '/LandingPage',
        name: 'LandingPage',
        component: LandingPage,
    }
];

const router = createRouter({
    history: createWebHistory(process.env.BASE_URL),
    routes,
});

export default router;