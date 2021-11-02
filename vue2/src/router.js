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
        title: 'Upload'
      },
      beforeEnter: (to, from, next) => {
        const user = store.state.auth.user
        if (user.isAuthorized) {
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
      meta: {
        title: 'Administration'
      },
      beforeEnter: (to, from, next) => {
        const user = store.state.auth.user
        if (user.isAdmin) {
          next()
        } else {
          next('/401')
        }
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
        title: '404 Not found'
      },
      props: route => ({
        text: 'Requested ' + route.fullPath + ' cannot be found'
      })
    }
  ]
})

router.afterEach(to => {
  // eslint-disable-next-line no-undef
  gtag('config', process.env.VUE_APP_GA, {
    page_path: to.fullPath,
    app_name: 'ANDS',
    send_page_view: true
  })
})

export default router
