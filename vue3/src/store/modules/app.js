import { api, CONFIG, pushMessage } from "../../helpers";
import { debounce } from "quasar";
import querystring from "querystring-es3";
import { notify } from "../../helpers";

const state = {
  find: {},
  uploaded: [],

  last: {
    count: 0,
    filename: null,
    date: new Date("1970-01-01").toISOString(),
    value: 1970,
  },
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
  clear: false,
  dark: false,

  snackbar: null,
};

const getters = {
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
};

const actions = {
  saveRecord: ({ commit, dispatch }, obj) => {
    if (obj.id) {
      api.put("edit/" + obj.id, obj).then((response) => {
        const obj = response.data.rec;
        commit("updateRecord", obj);
        commit("updateValues", obj);
      });
    } else {
      // publish
      api.put("edit", obj).then((response) => {
        const obj = response.data.rec;
        const diff = { verb: "add", size: obj.size };
        commit("addRecord", obj);
        commit("deleteUploaded", obj);
        commit("updateValues", obj);
        dispatch("bucketInfo", diff);
      });
    }
  },
  deleteRecord: ({ commit, dispatch }, obj) => {
    if (obj.id) {
      api
        .delete("delete/" + obj.id, { data: { foo: "bar" } })
        .then((response) => {
          if (response.data) {
            const diff = { verb: "del", size: obj.size };
            notify("info", `Successfully deleted ${obj.filename}`);
            commit("deleteRecord", obj);
            dispatch("fetchStat");
            dispatch("bucketInfo", diff);
          }
        })
        .catch((err) => {
          if (err.code === "ECONNABORTED") {
            notify("negative", "Fail to delete. Timeout error");
          }
        });
    } else {
      api
        .delete("remove/" + obj.filename, { data: { foo: "bar" } })
        .then((response) => {
          if (response.data) {
            notify("info", `Successfully deleted ${obj.filename}`);
            commit("deleteUploaded", obj);
          }
        })
        .catch((err) => {
          if (err.code === "ECONNABORTED") {
            notify("negative", "Fail to delete. Timeout error");
          }
        });
    }
  },
  changeFilter: ({ commit, dispatch }, payload) => {
    if (payload.reset) {
      commit("setClear", true);
      commit("setBusy", false); // interupt loading
      commit("resetPaginator");
      dispatch("fetchRecords", payload.pid);
    }
  },
  fetchRecords: ({ commit, state }, pid) => {
    if (state.busy) return;
    const params = Object.assign({}, state.find, {
      per_page: pid ? 2 * CONFIG.limit : CONFIG.limit,
    });
    if (state.next) params._page = state.next;
    const url = "search?" + querystring.stringify(params);

    commit("setError", null);
    commit("setBusy", true);
    api
      .get(url)
      .then((response) => {
        if (state.clear) {
          commit("resetObjects");
          commit("setClear", false);
        }
        if (response.data.objects && response.data.objects.length === 0) {
          commit("setError", 0);
        }
        if (response.error) commit("setError", response.error);
        commit("updateObjects", response.data);
        commit("setBusy", false);
      })
      .catch((err) => {
        notify("negative", `${err}`);
        commit("setBusy", false);
      });
  },
  fetchStat: ({ commit, dispatch, state }) => {
    api.get("counters").then((response) => {
      commit("setValues", response.data);
      if (state.bucket.count === 0) {
        dispatch("bucketInfo", { verb: "set" });
      }
    });
  },
  bucketInfo: debounce(({ dispatch }, param) => {
    dispatch("_bucketInfo", param);
  }, 2000),
  _bucketInfo: ({ commit, rootState }, param) => {
    /**
     * param: { verb: 'add|del|get', [size: int] }
     */
    if (param.verb === "get") {
      api.get(param.verb + "/bucket_info").then((response) => {
        commit("setBucket", response.data);
      });
    } else {
      api.put(param.verb + "/bucket_info", param).then((response) => {
        if (param.verb === "set") {
          pushMessage(rootState.auth.fcm_token, "DONE");
        }
        commit("setBucket", response.data);
      });
    }
  },
};

const mutations = {
  addUploaded(state, data) {
    state.uploaded = [...state.uploaded, data];
  },
  deleteUploaded(state, obj) {
    const idx = state.uploaded.findIndex(
      (item) => item.filename === obj.filename
    );
    if (idx > -1) state.uploaded.splice(idx, 1);
  },
  addRecord(state, obj) {
    const dates = state.objects.map((item) => item.date);
    const idx = dates.findIndex((date) => date < obj.date);
    state.objects.splice(idx, 0, obj);
  },
  updateRecord(state, obj) {
    if (state.objects && state.objects.length) {
      const idx = state.objects.findIndex((item) => item.id === obj.id);
      state.objects.splice(idx, 1, obj);
    }
  },
  deleteRecord(state, obj) {
    const idx = state.objects.findIndex((item) => item.id === obj.id);
    if (idx > -1) state.objects.splice(idx, 1);
  },
  saveFindForm(state, payload) {
    // if (Object.prototype.hasOwnProperty.call(payload, "year"))
    //   payload.year = +payload.year;
    // if (Object.prototype.hasOwnProperty.call(payload, "month"))
    //   payload.month = +payload.month;
    // if (Object.prototype.hasOwnProperty.call(payload, "day"))
    //   payload.day = +payload.day;
    state.find = { ...payload };
  },
  updateObjects(state, data) {
    if (state.pages[0] === "FP" && data._page === "FP") return;
    state.objects = [...state.objects, ...data.objects];
    state.pages = [...state.pages, data._page];
    state.next = data._next;
  },
  setClear(state, val) {
    state.clear = val;
  },
  resetObjects(state) {
    state.objects.length = 0;
  },
  resetPaginator(state) {
    state.pages.length = 0;
    state.next = null;
  },
  setBucket(state, obj) {
    state.bucket = { ...state.bucket, ...obj };
  },
  setValues(state, data) {
    CONFIG.photo_filter.forEach((field) => {
      if (Object.prototype.hasOwnProperty.call(data, field)) {
        if (field === "year") {
          const last = data.year[0];
          if (last) {
            state.last = {
              ...state.last,
              ...last,
            };
          }
        }
        state.values[field] = [
          ...Array.from(data[field], (c) => {
            return c.value;
          }),
        ];
      } else {
        state.values[field] = [];
      }
    });
  },
  updateValues(state, obj) {
    const lastFromState = new Date(state.last.date);
    const lastFromObject = new Date(obj.date);
    if (lastFromObject.getTime() > lastFromState.getTime()) {
      state.last = {
        ...state.last,
        ...{
          count: state.last.count + 1,
          filename: obj.filename,
          date: obj.date,
          value: lastFromObject.getFullYear(),
        },
      };
    }
    state.values.year = [...new Set([...state.values.year, 1 * obj.year])];
    if (obj.tags) {
      state.values.tags = [...new Set([...state.values.tags, ...obj.tags])];
    }
    if (obj.model) {
      state.values.model = [...new Set([...state.values.model, obj.model])];
    }
    if (obj.lens) {
      state.values.lens = [...new Set([...state.values.lens, obj.lens])];
    }
    state.values.email = [...new Set([...state.values.email, obj.email])];
  },
  updateValuesEmail(state, user) {
    state.values.email = [...new Set([...state.values.email, user.email])];
  },
  setBusy(state, val) {
    state.busy = val;
  },
  setError(state, val) {
    state.error = val;
  },
  toggleTheme(state, val) {
    state.dark = val;
  },
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations,
};
