import 'font-awesome-animation/css/font-awesome-animation.min.css'
import '@/style.css'

import { library } from '@fortawesome/fontawesome-svg-core'
import {
  faAngleDown,
  faCircleCheck,
  faCopy,
  faDownload,
  faEnvelope,
  faFileLines,
  faGlobe,
  faIdBadge,
  faInfoCircle,
  faLink,
  faNetworkWired,
  faPaperclip,
  faRoute,
  faSearch,
  faShieldHalved,
  faSpinner,
  faTriangleExclamation,
  faUpload
} from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { createPinia } from 'pinia'
import { createApp } from 'vue'

import router from '@/router'

library.add(
  faAngleDown,
  faCircleCheck,
  faCopy,
  faDownload,
  faEnvelope,
  faFileLines,
  faGlobe,
  faIdBadge,
  faInfoCircle,
  faLink,
  faNetworkWired,
  faPaperclip,
  faRoute,
  faSearch,
  faShieldHalved,
  faSpinner,
  faTriangleExclamation,
  faUpload
)
const pinia = createPinia()

import App from '@/App.vue'
import { initializeStores } from '@/store'

const app = createApp(App)

app.component('font-awesome-icon', FontAwesomeIcon)
app.use(router)
app.use(pinia)

initializeStores()

app.mount('#app')
