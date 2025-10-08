import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'home',
    component: () => import('../pages/Home.vue'),
  },
  {
    path: '/upload',
    name: 'upload',
    component: () => import('../pages/Upload.vue'),
  },
  {
    path: '/recommend',
    name: 'recommend',
    component: () => import('../pages/Recommend.vue'),
  },
  {
    path: '/report/:resume/:job',
    name: 'report',
    component: () => import('../pages/Report.vue'),
    props: true,
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: { name: 'home' },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  },
})

export default router
