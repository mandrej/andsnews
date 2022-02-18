import { CONFIG, api, firebase, pushMessage } from "../../helpers";
import { getAuth, signInWithPopup, GoogleAuthProvider } from "firebase/auth";
import { getMessaging, getToken } from "firebase/messaging";
import router from "../../router";

const auth = getAuth(firebase);
const messaging = getMessaging();
const provider = new GoogleAuthProvider();
provider.addScope("profile");
provider.addScope("email");

const state = {
  user: {},
  fcm_token: null,
};

const getters = {};
const actions = {
  signIn: ({ commit, dispatch, state }) => {
    if (state.user && state.user.uid) {
      auth.signOut().then(() => {
        commit("saveUser", {});
        const routeName = router.currentRoute.name;
        if (routeName === "add" || routeName === "admin") {
          router.replace({ name: "home" });
        }
      });
    } else {
      signInWithPopup(auth, provider)
        .then((response) => {
          const payload = {
            name: response.user.displayName,
            email: response.user.email,
            uid: response.user.uid,
            photo: response.user.photoURL,
            isAuthorized: true,
            isAdmin: CONFIG.admins.indexOf(response.user.uid) !== -1,
            lastLogin: Date.now(), // millis
          };
          commit("saveUser", payload);
          dispatch("updateUser", payload);
          dispatch("getPermission");
        })
        .catch((err) => {
          console.error(err.message);
        });
    }
  },
  updateUser: ({ commit }, user) => {
    api
      .post("user", { user: user })
      .then((response) => {
        if (response.data.success) {
          commit("app/updateValuesEmail", user, { root: true });
        }
      })
      .catch(() => console.error("update user failed"));
  },
  getPermission: ({ dispatch }) => {
    try {
      Notification.requestPermission().then((permission) =>
        dispatch("fetchToken", permission)
      );
    } catch (error) {
      // https://developer.mozilla.org/en-US/docs/Web/API/Notifications_API/Using_the_Notifications_API
      Notification.requestPermission(function (permission) {
        dispatch("fetchToken", permission);
      });
    }
  },
  fetchToken: ({ commit, state, dispatch }, permission) => {
    if (permission === "granted") {
      return getToken(messaging, { vapidKey: CONFIG.firebase.vapidKey })
        .then((token) => {
          if (token && token !== state.fcm_token) {
            commit("setToken", token);
            // TODO not sure
            if (state.user && state.user.uid) {
              dispatch("addRegistration");
            }
          }
        })
        .catch(function (err) {
          console.error("Unable to retrieve token ", err);
        });
    }
  },
  addRegistration: ({ state }) => {
    api
      .put("user/register", { uid: state.user.uid, token: state.fcm_token })
      .then()
      .catch((err) => console.error(err));
  },
  // eslint-disable-next-line no-unused-vars
  sendNotifications: ({ state }, msg) => {
    api.get("registrations").then((response) => {
      pushMessage(response.data, msg);
    });
  },
};
const mutations = {
  saveUser(state, payload) {
    state.user = { ...payload };
  },
  setToken(state, val) {
    state.fcm_token = val;
  },
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations,
};
