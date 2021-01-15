import Vue from 'vue'
import Router from 'vue-router'
import Home from '@/views/Home'
import List from '@/views/List'
import store from './store'

const Add = () => import(/* webpackChunkName: "add" */ '@/views/Add')
const Admin = () => import(/* webpackChunkName: "admin" */ '@/views/Admin')
const Err = () => import(/* webpackChunkName: "error" */ '@/views/Err')

Vue.use(Router)

const router = new Router({
  mode: 'history',
  scrollBehavior (to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { x: 0, y: 0 }
    }
  },
  routes: [
    {
      path: '/',
      name: 'home',
      component: Home
    },
    {
      path: '/list',
      name: 'list',
      component: List
    },
    {
      path: '/add',
      name: 'add',
      component: Add,
      meta: {
        title: 'Upload',
        requiresAuth: true
      }
    },
    {
      path: '/admin',
      name: 'admin',
      component: Admin,
      meta: {
        title: 'Administration',
        requiresAuth: true
      }
    },
    {
      path: '/401',
      component: Err,
      meta: {
        title: '401 Insufficient credentials',
        requiresAuth: true
      },
      props: {
        text: 'You cannot access this page'
      }
    },
    {
      path: '*',
      component: Err,
      meta: {
        title: '404 Not found',
      },
      props: route => ({
        text: 'Requested ' + route.fullPath + ' cannot be found'
      })
    }
  ]
})

router.beforeEach((to, from, next) => {
  if (to.matched.some(record => record.meta.requiresAuth)) {
    const user = store.state.auth.user
    if (to.name === 'add' && user.isAuthorized) {
      next()
    } else if (to.name === 'admin' && user.isAdmin) {
      next()
    } else {
      next('/401')
    }
  } else {
    next() // make sure to always call next()!
  }
})

router.afterEach((to) => {
  // eslint-disable-next-line no-undef
  gtag('config', process.env.VUE_APP_GA, {
    page_path: to.fullPath,
    app_name: 'ANDS',
    send_page_view: true,
  })
})

export default router
