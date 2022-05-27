# Running for development

1. Create a `settings.js` file in `frontend/public` with the following content:

```js
SETTINGS = {
    runPyrightEndpoint: "http://127.0.0.1:8000/pyright",
    downloadCodeEndpoint: "http://127.0.0.1:8000/download_code",
    generateDownloadLinkEndpoint: "http://127.0.0.1:8000/download_link",
    baseUrl: "http://127.0.0.1:5000",
}
```

2. `npm run dev`
