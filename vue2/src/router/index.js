import Vue from 'vue'
import Router from 'vue-router'
import Home from '@/components/Home'
import Add from '@/components/Add'
import Search from '@/components/Search'
import Admin from '@/components/Admin'

Vue.use(Router)

export default new Router({
  mode: 'history',
  routes: [
    {
      path: '/',
      name: 'home',
      component: Home
    },
    {
      path: '/add',
      name: 'add',
      component: Add,
      meta: {
        back: 'home'
      }
    },
    {
      path: '/admin',
      name: 'admin',
      component: Admin,
      meta: {
        back: 'home'
      }
    },
    {
      path: '/search/:term',
      name: 'search',
      component: Search
    }
  ]
})
