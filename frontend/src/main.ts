import App from "./App.svelte"

const app = new App({
    target: document.body,
    props: {
        runPyrightEndpoint: window.SETTINGS.runPyrightEndpoint,
        downloadCodeEndpoint: window.SETTINGS.downloadCodeEndpoint,
        generateDownloadLinkEndpoint: window.SETTINGS.generateDownloadLinkEndpoint,
        baseUrl: window.SETTINGS.baseUrl,
    },
})

export default app
