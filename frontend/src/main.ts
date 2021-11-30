import App from "./App.svelte"

const app = new App({
    target: document.body,
    props: {
        apiEndpoint: window.SETTINGS.apiEndpoint,
    },
})

export default app
