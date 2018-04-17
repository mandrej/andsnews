import Vue from 'vue'
import Router from 'vue-router'
import Home from '@/components/Home'
import Item from '@/components/Item'
import Add from '@/components/Add'
import Find from '@/components/Find'
import Search from '@/components/Search'
import Edit from '@/components/Edit'

Vue.use(Router)

export default new Router({
  mode: 'history',
  // scrollBehavior (to, from, savedPosition) {
  //   if (savedPosition) {
  //     return savedPosition
  //   } else {
  //     return { x: 0, y: 0 }
  //   }
  // },
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
      path: '/find',
      name: 'find',
      component: Find
    },
    {
      path: '/search/:term',
      name: 'search',
      component: Search
    },
    {
      path: '/view/:id',
      name: 'item',
      component: Item
    },
    {
      path: '/edit/:id',
      name: 'edit',
      component: Edit
    }
  ]
})
