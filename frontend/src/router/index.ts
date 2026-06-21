import { createRouter, createWebHistory } from 'vue-router'

import GenreListView from '../views/GenreListView.vue'
import ShopDetailView from '../views/ShopDetailView.vue'
import ShopFormView from '../views/ShopFormView.vue'
import ShopListView from '../views/ShopListView.vue'
import ShopMapView from '../views/ShopMapView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'list', component: ShopListView },
    { path: '/map', name: 'map', component: ShopMapView },
    { path: '/genres', name: 'genres', component: GenreListView },
    { path: '/shops/new', name: 'create', component: ShopFormView },
    { path: '/shops/:id/edit', name: 'edit', component: ShopFormView, props: true },
    { path: '/shops/:id', name: 'detail', component: ShopDetailView, props: true },
  ],
})

export default router
