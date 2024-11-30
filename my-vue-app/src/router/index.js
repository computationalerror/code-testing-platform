import { createRouter, createWebHistory } from 'vue-router';
import HomePage from '@/components/HomePage.vue';
import LoginPage from '@/components/LoginPage.vue';
import RegisterPage from '@/components/RegisterPage.vue';
import ForgotPassword from '@/components/ForgotPassword.vue';
import PreferencePage from '@/components/PreferencePage.vue';
import LandingPage from '@/components/LandingPage.vue';
import TopicPage from '@/components/TopicPage.vue';
import SampleOne from "@/components/SampleOne.vue";
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
    {
        path: '/TopicPage',
        name: 'TopicPage',
        component: TopicPage,
    },
    {
        path: '/SampleOne',
        name: 'SampleOne',
        component: SampleOne,
    },
    {
        // Add a dynamic parameter ':topic' to pass the selected topic
        path: '/SampleOne/:topic',
        name: 'SampleOne',
        component: SampleOne,
        props: true, // Pass the route parameter as a prop to the component
    },
]

const router = createRouter({
    history: createWebHistory(process.env.BASE_URL),
    routes,
});

export default router;