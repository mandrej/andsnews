import Vue from 'vue'
import Router from 'vue-router'
import Home from '@/views/Home'
import createStore from './store'

const Admin = () => import(/* webpackChunkName: "admin" */ '@/views/Admin')
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
      component: Home
    },
    {
      path: '/admin',
      name: 'admin',
      component: Admin,
      beforeEnter: (to, from, next) => {
        const store = createStore()
        if (store.state.All.user.isAdmin) {
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
        text: 'Page you requested cannot be found'
      }
    }
  ]
})
