/// <reference types="svelte" />

interface Settings {
    runPyrightEndpoint: string
    downloadCodeEndpoint: string
}

interface Window {
    SETTINGS: Settings
}
