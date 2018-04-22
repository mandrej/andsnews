<template>
  <div>
    <Edit :visible="editdForm" :rec="current" @close="editdForm = false"></Edit>
    <Item :visible="showItem" :rec="current" @close="showItem = false"></Item>

    <v-dialog v-model="dialog" max-width="300px" lazy>
      <v-card>
        <v-card-title class="headline">
          No photos for current filter / search
        </v-card-title>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="secondary" flat @click.stop="dialog = false; $router.push({name: 'home'})">Close</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <div class="grid">
      <div v-masonry
        transition-duration="0.6s"
        item-selector=".grid-item"
        horizontal-order="true"
        column-width=".grid-sizer"
        gutter=".gutter-sizer">
        <div class="grid-sizer"></div>
        <div class="gutter-sizer"></div>
        <div v-masonry-tile
          class="grid-item"
          v-for="item in objects"
          :key="item.safekey">
          <v-card>
            <v-card-media :src="getImgSrc(item, 's')" @click="showDetail(item)" height="300px"></v-card-media>
            <v-card-title primary-title>
              <div>
                <h3 class="headline mb-0">{{item.headline}}</h3>
                <div>{{item.date}}</div>
              </div>
            </v-card-title>
            <v-card-actions v-if="user.isAuthorized">
              <v-btn v-if="user.isAdmin" flat color="secondary" @click="deleteRecord(item)">Delete</v-btn>
              <v-spacer></v-spacer>
              <v-btn flat color="primary" @click="showEditdForm(item)">Edit</v-btn>
            </v-card-actions>
          </v-card>
        </div>
      </div>

      <mugen-scroll
        :handler="loadMore"
        :should-handle="!busy"
        :threshold="threshold"
        handle-on-mount
        scroll-container="grid">
        <v-progress-linear v-show="busy" :indeterminate="true"></v-progress-linear>
      </mugen-scroll>
    </div>
  </div>
</template>

<script>
import Vue from 'vue'
import { mapState } from 'vuex'
import { VueMasonryPlugin } from 'vue-masonry'
import MugenScroll from 'vue-mugen-scroll'
import Item from './Item'
import Edit from './Edit'
import common from '../../helpers/mixins'

Vue.use(VueMasonryPlugin)

export default {
  name: 'Home',
  components: {
    MugenScroll,
    Item,
    Edit
  },
  mixins: [ common ],
  data: () => ({
    threshold: 0,
    dialog: false,
    current: {},
    showItem: false,
    editdForm: false
  }),
  computed: {
    ...mapState(['user', 'objects', 'pages', 'next', 'filter', 'busy'])
  },
  watch: {
    busy (newVal, oldVal) {
      if (!newVal && this.objects.length === 0) {
        this.dialog = true
      }
    }
  },
  methods: {
    loadMore () {
      if (this.objects.length === 0) {
        this.$store.dispatch('loadList')
      } else if (this.next && this.pages.indexOf(this.next) === -1) {
        this.$store.dispatch('loadList', this.next)
      }
    },
    showDetail (rec) {
      this.current = rec
      this.showItem = true
    },
    showEditdForm (rec) {
      this.current = rec
      this.editdForm = true
    },
    deleteRecord (rec) {
      this.$store.dispatch('deleteRecord', rec)
    }
  }
}
</script>

<style lang="scss" scoped>
.grid {
  margin: 0;
  padding: 16px;
  padding-right: 0;
}
.grid-sizer, .grid-item {
  width: calc(100% / 4 - 16px);
  @media (max-width: 1280px) {
    width: calc(100% / 3 - 16px);
  }
  @media (max-width: 960px) {
    width: calc(100% / 2 - 16px);
  }
  @media (max-width: 600px) {
    width: calc(100% - 16px);
  }
}
.grid-item {
  margin-bottom: 16px;
}
.gutter-sizer {
  width: 16px;
}
</style>
