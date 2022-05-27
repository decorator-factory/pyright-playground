/// <reference types="svelte" />

interface Settings {
    runPyrightEndpoint: string
    downloadCodeEndpoint: string
    generateDownloadLinkEndpoint: string
    baseUrl: string
}

interface Window {
    SETTINGS: Settings
}
