/* eslint-disable no-unused-vars */
import { defineStore } from "pinia";
import { CONFIG, api, firebase, pushMessage } from "../helpers";
import { getAuth, signInWithPopup, GoogleAuthProvider } from "firebase/auth";
import { useAppStore } from "./app";
import { getMessaging, getToken } from "firebase/messaging";
import router from "../router";

const auth = getAuth(firebase);
const messaging = getMessaging();
const provider = new GoogleAuthProvider();
provider.addScope("profile");
provider.addScope("email");

export const useAuthStore = defineStore("auth", {
  state: () => ({
    user: {},
    fcm_token: null,
  }),
  getters: {
    isAdmin: (state) => {
      if (state.user && state.user.isAdmin) {
        return true;
      }
      return false;
    },
    isAuthorized: (state) => {
      if (state.user && state.user.isAuthorized) {
        return true;
      }
      return false;
    },
  },
  actions: {
    signIn() {
      if (this.user && this.user.uid) {
        auth.signOut().then(() => {
          this.user = {};
          const routeName = router.currentRoute.name;
          if (routeName === "add" || routeName === "admin") {
            router.push({ name: "home" });
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
            this.user = { ...payload };
            this.updateUser(payload);
            this.getPermission();
          })
          .catch((err) => {
            console.error(err.message);
          });
      }
    },
    async updateUser(user) {
      try {
        const response = await api.post("user", { user: user });
        if (response.data.success) {
          const app = useAppStore();
          app.updateValuesEmail(user);
        }
      } catch (err) {
        console.error("update user failed");
      }
    },
    getPermission() {
      try {
        Notification.requestPermission().then((permission) =>
          this.fetchToken(permission)
        );
      } catch (error) {
        // https://developer.mozilla.org/en-US/docs/Web/API/Notifications_API/Using_the_Notifications_API
        Notification.requestPermission(function (permission) {
          this.fetchToken(permission);
        });
      }
    },
    fetchToken(permission) {
      if (permission === "granted") {
        return getToken(messaging, { vapidKey: CONFIG.firebase.vapidKey })
          .then((token) => {
            if (token) {
              console.log(token);
              if (this.fcm_token === null || token !== this.fcm_token) {
                this.fcm_token = token;
                if (this.user && this.user.uid) {
                  this.addRegistration();
                }
              }
            }
          })
          .catch(function (err) {
            console.error("Unable to retrieve token ", err);
          });
      }
    },
    addRegistration() {
      api
        .put("user/register", { uid: this.user.uid, token: this.fcm_token })
        .then()
        .catch((err) => console.error(err));
    },
    // eslint-disable-next-line no-unused-vars
    sendNotifications(msg) {
      api.get("registrations").then((response) => {
        pushMessage(response.data, msg);
      });
    },
  },
  persist: {
    paths: ["user", "fcm_token"],
    beforeRestore: (context) => {
      console.log("Before hydration...", context);
    },
    afterRestore: (context) => {
      console.log("After hydration...", context);
    },
  },
});
