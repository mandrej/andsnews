/* eslint-disable no-unused-vars */
import { defineStore } from "pinia";
import { CONFIG, api, pushMessage, notify } from "../helpers";
import { useAuthStore } from "./auth";
import querystring from "querystring-es3";

export const useAppStore = defineStore("app", {
  state: () => ({
    find: {},

    uploaded: [],
    percentage: 0,

    last: null,
    bucket: {
      size: 0,
      count: 0,
    },
    values: {},

    objects: [],
    pages: [],
    next: null,
    error: null,

    busy: false,
    current: {},
  }),
  getters: {
    counter: (state) => {
      return { count: state.objects.length, more: state.next };
    },

    nickNames: (state) => {
      if (state.values && state.values.email) {
        return state.values.email.map((email) => {
          return email.match(/[^@]+/)[0].split(".")[0];
        });
      }
      return [];
    },
    objectsByDate: (state) => {
      return state.objects.reduce((groups, obj) => {
        const date = obj.date.slice(0, 10);
        if (!groups[date]) {
          groups[date] = [];
        }
        groups[date].push(obj);
        return groups;
      }, {});
    },
  },
  actions: {
    deleteUploaded(obj) {
      const idx = this.uploaded.findIndex(
        (item) => item.filename === obj.filename
      );
      if (idx > -1) this.uploaded.splice(idx, 1);
    },
    async bucketInfo(param) {
      /**
       * param: { verb: 'add|del|get', [size: int] }
       */
      let response;
      if (param.verb === "get") {
        response = await api.get(param.verb + "/bucket_info");
        this.bucket = { ...this.bucket, ...response.data };
      } else {
        const auth = useAuthStore();
        response = await api.put(param.verb + "/bucket_info", param);
        if (param.verb === "set") {
          pushMessage(auth.fcm_token, "Cloud Bucket Info done");
        }
        this.bucket = { ...this.bucket, ...response.data };
      }
    },
    saveRecord(obj) {
      if (obj.id) {
        api.put("edit/" + obj.id, obj).then((response) => {
          const obj = response.data.rec;
          if (this.objects && this.objects.length) {
            const idx = this.objects.findIndex((item) => item.id === obj.id);
            this.objects.splice(idx, 1, obj);
          }
          // this.updateValues(obj);
        });
      } else {
        // publish
        api.put("edit", obj).then((response) => {
          const obj = response.data.rec;
          const diff = { verb: "add", size: obj.size };
          // addRecord
          const dates = this.objects.map((item) => item.date);
          const idx = dates.findIndex((date) => date < obj.date);
          this.objects.splice(idx, 0, obj);

          this.deleteUploaded(obj);
          // this.updateValues(obj);
          this.bucketInfo(diff);
        });
      }
    },
    deleteRecord(obj) {
      if (obj.id) {
        api
          .delete("delete/" + obj.id, { data: { foo: "bar" } })
          .then((response) => {
            if (response.data) {
              const diff = { verb: "del", size: obj.size };
              notify({
                type: "info",
                message: `Successfully deleted ${obj.filename}`,
              });
              const idx = this.objects.findIndex((item) => item.id === obj.id);
              if (idx > -1) this.objects.splice(idx, 1);

              this.fetchStat();
              this.bucketInfo(diff);
            }
          })
          .catch((err) => {
            if (err.code === "ECONNABORTED") {
              notify({
                type: "negative",
                message: "Fail to delete. Timeout error",
              });
            }
          });
      } else {
        api
          .delete("remove/" + obj.filename, { data: { foo: "bar" } })
          .then((response) => {
            if (response.data) {
              notify({
                type: "info",
                message: `Successfully deleted ${obj.filename}`,
              });
              this.deleteUploaded(obj);
            }
          })
          .catch((err) => {
            if (err.code === "ECONNABORTED") {
              notify({
                type: "negative",
                message: "Fail to delete. Timeout error",
              });
            }
          });
      }
    },
    resetObjects() {
      this.objects.length = 0;
      this.pages.length = 0;
      this.next = null;
    },
    updateObjects(data) {
      if (this.pages[0] === "FP" && data._page === "FP") return;
      this.objects = [...this.objects, ...data.objects];
      this.pages = [...this.pages, data._page];
      this.next = data._next;
    },
    fetchRecords(reset = false) {
      if (this.busy) return;
      const params = Object.assign({}, this.find, { per_page: CONFIG.limit });
      if (this.next && !reset) params._page = this.next;
      const url = "search?" + querystring.stringify(params);

      this.error = null;
      this.busy = true;
      api
        .get(url)
        .then((response) => {
          if (response.error) {
            this.error = response.error;
          } else if (
            response.data.objects &&
            response.data.objects.length === 0
          ) {
            this.error = 0;
          }
          if (reset) this.resetObjects(); // late reset
          this.updateObjects(response.data);
          this.busy = false;
        })
        .catch((err) => {
          notify({ type: "negative", message: `${err}` });
          this.busy = false;
        });
    },
    setValues(data) {
      CONFIG.photo_filter.forEach((field) => {
        if (Object.prototype.hasOwnProperty.call(data, field)) {
          if (field === "year") {
            const obj = data.year[0];
            this.last = obj.filename;
          }
          this.values[field] = [
            ...Array.from(data[field], (c) => {
              return c.value;
            }),
          ];
        } else {
          this.values[field] = [];
        }
      });
    },
    updateValues(obj) {
      const lastFromState = new Date(this.last.date);
      const lastFromObject = new Date(obj.date);
      if (lastFromObject.getTime() > lastFromState.getTime()) {
        this.last = obj.filename;
      }
    },
    fetchStat() {
      api.get("counters").then((response) => {
        this.setValues(response.data);
        if (this.bucket.count === 0) {
          this.bucketInfo({ verb: "set" });
        } else {
          this.bucketInfo({ verb: "get" });
        }
      });
    },
  },
  persist: {
    key: "a",
    paths: [
      "find",
      "last",
      "bucket",
      "values",
      "uploaded",
      "objects",
      "pages",
      "next",
      "current",
    ],
    // beforeRestore: (context) => {
    //   console.log("Before hydration...", context);
    // },
    // afterRestore: (context) => {
    //   console.log("After hydration...", context);
    // },
  },
});
