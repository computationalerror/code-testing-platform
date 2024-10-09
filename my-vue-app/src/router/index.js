import { createRouter, createWebHistory } from 'vue-router';
import HomePage from '@/components/HomePage.vue';
import LoginPage from '@/components/LoginPage.vue';
import RegisterPage from '@/components/RegisterPage.vue';
import ForgotPassword from '@/components/ForgotPassword.vue';
import PreferencePage from '@/components/PreferencePage.vue';
import LandingPage from '@/components/LandingPage.vue';

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
    },
];

const router = createRouter({
    history: createWebHistory(process.env.BASE_URL),
    routes,
});

export default router;