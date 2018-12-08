import Vue from 'vue'
import Router from 'vue-router'
import Home from '@/views/Home'
import Add from '@/views/Add'
import createStore from './store'

const store = createStore()
const Admin = () => import(/* webpackChunkName: "admin" */ '@/views/Admin')
// const Item = () => import(/* webpackChunkName: "item" */ '@/views/Item')
const Err = () => import(/* webpackChunkName: "error" */ '@/views/Err')

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
      path: '/list/:qs',
      name: 'list',
      component: Home,
      props: true
    },
    // {
    //   path: '/item/:safekey',
    //   name: 'item',
    //   component: Item,
    //   props: true
    // },
    {
      path: '/add',
      name: 'add',
      component: Add,
      beforeEnter: (to, from, next) => {
        if (store.state.auth.user.isAuthorized) {
          next()
        } else {
          next('/401')
        }
      }
    },
    {
      path: '/admin',
      name: 'admin',
      component: Admin,
      beforeEnter: (to, from, next) => {
        if (store.state.auth.user.isAdmin) {
          next()
        } else {
          next('/401')
        }
      }
    },
    {
      path: '/401',
      component: Err,
      props: {
        title: '401 Insufficient credentials',
        text: 'You cannot access this page'
      }
    },
    {
      path: '*',
      component: Err,
      props: {
        title: '404 Not found',
        text: 'Requested page cannot be found'
      }
    }
  ]
})
