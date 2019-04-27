import Vue from 'vue'
import Router from 'vue-router'
import Home from '@/views/Home'
import Add from '@/views/Add'
import createStore from './store'

const Admin = () => import(/* webpackChunkName: "admin" */ '@/views/Admin')
const Err = () => import(/* webpackChunkName: "error" */ '@/views/Err')

function requireAuth (to, from, next) {
  const store = createStore()
  const user = store.state.auth.user
  if (to.name === 'add' && user.isAuthorized) {
    next()
  } else if (to.name === 'admin' && user.isAdmin) {
    next()
  } else {
    next('/401')
  }
}

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
      path: '/list',
      name: 'list',
      component: Home,
      props: route => ({
        text: route.query.text,
        tags: route.query.tags,
        year: route.query.year,
        month: route.query.month,
        model: route.query.model,
        email: route.query.email
      })
    },
    {
      path: '/add',
      name: 'add',
      component: Add,
      beforeEnter: requireAuth
    },
    {
      path: '/admin',
      name: 'admin',
      component: Admin,
      beforeEnter: requireAuth
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
