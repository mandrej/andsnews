import gql from 'graphql-tag'

export const Values = gql`query { values { year tags model color author } }`
export const Filter = gql`query {
  count
  filters { count name fieldName servingUrl }
}`
export const Result = gql`query ($find: String!, $page: String, $perPage: Int!) {
  result (find: $find, page: $page, perPage: $perPage) {
    page
    nextPage
    error
    objects {
      id
      kind slug headline author date year tags
      aperture shutter focalLength model lens iso color
      dim filename servingUrl
    }
  }
}`
export const Remove = gql`mutation ($id: String!) {
  remove (id: $id) { ok }
}`
export const Update = gql`mutation ($id: String!, $photoData: PhotoInput!) {
  update (id: $id, photoData: $photoData) {
    ok
    photo {
      kind slug headline author date year tags
      aperture shutter focalLength model lens iso color
      dim filename servingUrl
    }
  }
}`
