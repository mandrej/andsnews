/* eslint no-console: ["error", { allow: ["warn", "error"] }] */
// export const RESET = 'RESET';
import apolloProvider from '@/helpers/apollo'
import { Values, Filter, Result, Update, Remove } from '@/helpers/queries'

const LIMIT = 24
const apollo = apolloProvider.defaultClient

const initialState = {
  find: {},
  filter: {},
  uploaded: [],

  menu: [],
  objects: [],
  pages: [],
  next: null,
  error: '',
  values: {},

  total: null, // menu
  count: null,

  busy: false,
  clear: false
}
const actions = {
  // reset: ({ commit }) => commit(RESET),
  saveFindForm: ({ commit }, payload) => commit('SAVE_FIND_FORM', payload),
  changeFilter: ({ commit }, payload) => {
    commit('CHANGE_FILTER', payload)
    if (payload.field) {
      commit('SET_CLEAR', true)
      commit('SET_BUSY', false) // interupt loading
      commit('RESET_PAGINATOR')
    }
  },
  addRecord: async ({ commit }, obj) => {
    const response = await apollo.mutate({
      mutation: Update,
      variables: {
        id: obj.id,
        photoData: {
          kind: obj.kind,
          slug: obj.slug,
          headline: obj.headline,
          author: obj.author,
          date: obj.date,
          year: obj.year,
          tags: obj.tags,
          aperture: obj.aperture,
          shutter: obj.shutter,
          focalLength: obj.focalLength,
          model: obj.model,
          lens: obj.lens,
          iso: obj.iso
        }
      },
      update: (cache, { data: { update } }) => {
        if (update.ok) {
          cache.data.set(`PhotoType:${obj.id}`, update.photo)
        }
      },
      refetchQueries: [
        { query: Filter }
      ]
    })
    if (response.data.update.ok) {
      commit('ADD_UPLOADED', obj)
      commit('ADD_RECORD', obj)
    }
  },
  saveRecord: async ({ commit, state }, obj) => {
    const response = await apollo.mutate({
      mutation: Update,
      variables: {
        id: obj.id,
        photoData: {
          kind: obj.kind,
          slug: obj.slug,
          headline: obj.headline,
          author: obj.author,
          date: obj.date,
          year: obj.year,
          tags: obj.tags,
          aperture: obj.aperture,
          shutter: obj.shutter,
          focalLength: obj.focalLength,
          model: obj.model,
          lens: obj.lens,
          iso: obj.iso
        }
      },
      update: (cache, { data: { update } }) => {
        if (update.ok) {
          cache.data.set(`PhotoType:${obj.id}`, update.photo)
        }
      },
      refetchQueries: [
        { query: Filter },
        { query: Values },
        { query: Result,
          variables: {
            find: state.filter.value,
            page: state.next,
            perPage: LIMIT
          }
        }
      ]
    })
    if (response.data.update.ok) {
      const newObj = response.data.update.photo
      newObj['id'] = obj.id
      commit('UPDATE_RECORD', newObj)
      commit('DELETE_UPLOADED', newObj)
      commit('UPDATE_VALUES', newObj)
    }
  },
  deleteRecord: async ({ commit }, obj) => {
    const response = await apollo.mutate({
      mutation: Remove,
      variables: {
        id: obj.id
      },
      update: (cache, { data: { remove } }) => {
        if (remove.ok) {
          cache.data.delete(`PhotoType:${obj.id}`)
        }
      },
      refetchQueries: [
        { query: Filter },
        { query: Values }
      ]
    })
    if (response.data.remove.ok) {
      commit('DELETE_RECORD', obj)
      commit('DELETE_UPLOADED', obj)
    }
  },
  fetchMenu: async ({ commit }) => {
    const response = await apollo.query({
      query: Filter
    })
    commit('UPDATE_MENU', response.data)
  },
  fetchRecords: async ({ commit, state }) => {
    // if (state.busy) return
    commit('SET_ERROR', '')
    commit('SET_BUSY', true)
    const filter = { ...state.filter }
    const response = await apollo.query({
      query: Result,
      variables: {
        find: filter.value,
        page: state.next,
        perPage: LIMIT
      }
    })
    if (state.clear) {
      commit('RESET_RECORDS')
      commit('SET_CLEAR', false)
    }
    commit('UPDATE_RECORDS', response.data)
    if (response.error) commit('SET_ERROR', response.error)
    commit('SET_BUSY', false)
  },
  fetchValues: async ({ commit }) => {
    const response = await apollo.query({
      query: Values
    })
    commit('SET_VALUES', response.data)
  }
}
const mutations = {
  // [RESET]: state => ({ ...initialState }), // eslint-disable-line no-unused-vars
  SAVE_FIND_FORM (state, payload) {
    state.find = payload
  },
  CHANGE_FILTER (state, payload) {
    state.filter = payload
  },
  UPDATE_MENU (state, data) {
    state.total = data.count
    state.menu = [...data.filters]
  },
  ADD_RECORD (state, obj) {
    const dates = state.objects.map(item => item.date)
    const idx = dates.findIndex(date => date < obj.date)
    state.objects.splice(idx, 0, obj)
    state.count++
    state.total++
  },
  ADD_UPLOADED (state, data) {
    state.uploaded = [...state.uploaded, data]
  },
  UPDATE_RECORDS (state, data) {
    if (state.pages[0] === 'FP' && data.result.page === 'FP') return
    state.objects = [...state.objects, ...data.result.objects]
    state.pages = [...state.pages, data.result.page]
    state.next = data.result.nextPage
    state.count = state.objects.length
  },
  UPDATE_RECORD (state, obj) {
    const idx = state.objects.findIndex(item => item.id === obj.id)
    state.objects.splice(idx, 1, obj)
  },
  RESET_RECORDS (state) {
    state.objects.length = 0
  },
  RESET_PAGINATOR (state) {
    state.pages.length = 0
    state.next = null
  },
  DELETE_RECORD (state, obj) {
    const idx = state.objects.findIndex(item => item.id === obj.id)
    if (idx > -1) state.objects.splice(idx, 1)
    state.count--
    state.total--
  },
  DELETE_UPLOADED (state, obj) {
    const idx = state.uploaded.findIndex(item => item.id === obj.id)
    if (idx > -1) state.uploaded.splice(idx, 1)
  },
  UPDATE_VALUES (state, obj) {
    state.values.year = [...new Set([...state.values.year, 1 * obj.year])]
    state.values.tags = [...new Set([...state.values.tags, ...obj.tags])]
    state.values.color = [...new Set([...state.values.color, obj.color])]
    state.values.author = [...new Set([...state.values.author, obj.author])]
    if (obj.model) state.values.model = [...new Set([...state.values.model, obj.model])]
  },
  SET_VALUES (state, data) {
    state.values = data.values
  },
  SET_CLEAR (state, val) {
    state.clear = val
  },
  SET_BUSY (state, val) {
    state.busy = val
  },
  SET_ERROR (state, val) {
    state.error = val
  }
}

export default {
  namespaced: true,
  state: initialState,
  mutations,
  actions
}
