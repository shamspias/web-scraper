import {createRouter, createWebHistory} from 'vue-router'
import HomePage from '../views/HomePage.vue'
import JobDetailsPage from '../views/JobDetailsPage.vue'

const routes = [
    {
        path: '/',
        name: 'Home',
        component: HomePage
    },
    {
        path: '/job/:id',
        name: 'JobDetails',
        component: JobDetailsPage
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

export default router