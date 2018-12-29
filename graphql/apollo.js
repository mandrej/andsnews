import Vue from 'vue'
import { ApolloClient } from 'apollo-client'
import { HttpLink } from 'apollo-link-http'
import { InMemoryCache } from 'apollo-cache-inmemory'
import VueApollo from 'vue-apollo'

const httpLink = new HttpLink({
  uri: '/graphql'
})
export const apolloClient = new ApolloClient({
  link: httpLink,
  cache: new InMemoryCache(),
  connectToDevTools: true
})
const apolloProvider = new VueApollo({
  defaultClient: apolloClient
})
Vue.use(VueApollo)

export default apolloProvider
