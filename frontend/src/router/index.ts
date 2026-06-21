import { createRouter, createWebHistory } from 'vue-router'

import ShopFormView from '../views/ShopFormView.vue'
import ShopListView from '../views/ShopListView.vue'
import ShopMapView from '../views/ShopMapView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'list', component: ShopListView },
    { path: '/map', name: 'map', component: ShopMapView },
    { path: '/shops/new', name: 'create', component: ShopFormView },
    { path: '/shops/:id/edit', name: 'edit', component: ShopFormView, props: true },
  ],
})

export default router
