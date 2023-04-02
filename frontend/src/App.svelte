<script lang="ts">
    import CodeMirror from "./editor/CodeMirror.svelte"
    import type { Editor } from "./editor"
    import type { PyrightOutput } from "./pyrightTypes"

    import { onMount } from "svelte"

    export let runPyrightEndpoint: string
    export let downloadCodeEndpoint: string
    export let generateDownloadLinkEndpoint: string
    export let baseUrl: string

    const lineAndColToPos = (line: number, col: number, code: string) => {
        const lines = code.split("\n")
        if (lines.length < line) return code.length - 1
        const lengthSoFar = lines
            .slice(0, line + 1)
            .reduce((a, line) => a + line.length, 0)
        return lengthSoFar + col
    }

    let lastUpdatedMs = Date.now() - 500
    let updateTimeoutId: any = -1
    let editor: Editor

    const fetchAndApplyPyrightDiagnostic = async () => {
        const code = editor.read()
        const resp = await fetch(runPyrightEndpoint, {
            method: "POST",
            body: JSON.stringify({ code }),
            headers: {
                "Content-Type": "application/json",
            },
        })
        const pyrightOutput: PyrightOutput = await resp.json()

        editor.applyDiagnostics(pyrightOutput.generalDiagnostics)
    }

    const updateEditor = async () => {
        const diff = Date.now() - lastUpdatedMs
        if (diff < 500) {
            if (updateTimeoutId !== -1) clearTimeout(updateTimeoutId)
            updateTimeoutId = setTimeout(updateEditor, 500 - diff)
            return
        }
        lastUpdatedMs = Date.now()
        await fetchAndApplyPyrightDiagnostic()
    }

    const downloadCode = async () => {
        const { search } = new URL(document.location.href)
        if (!search.trim()) return

        const resp = await fetch(`${downloadCodeEndpoint}${search}`)
        if (resp.status !== 200) {
            // TODO: handle error
            return
        }
        editor.view.dispatch({
            changes: {
                from: 0,
                to: editor.view.state.doc.length,
            },
        })
        editor.view.dispatch({
            changes: {
                from: 0,
                insert: await resp.text(),
            },
        })
    }

    const generatePermalink = async () => {
        const resp = await fetch(`${generateDownloadLinkEndpoint}`, {
            method: 'POST',
            body: JSON.stringify({ base_url: baseUrl, code: editor.read() }),
            headers: {
                'Content-Type': 'application/json',
            }
        })
        const {download_link: downloadLink} = await resp.json()
        window.location.href = downloadLink
    }

    onMount(async () => {
        await downloadCode()

        editor.onUpdate(async (update) => {
            if (!update.docChanged) return

            await updateEditor()
        })

        await updateEditor()
    })
</script>

<main>
    <div class="title">Pyright playground</div>
    <div class="controls">
        <button on:click={generatePermalink} class="generate-permalink">Generate permalink</button>
        <a href="https://github.com/decorator-factory/pyright-playground">
            <button class="github">Star or fork on GitHub</button>
        </a>
    </div>
    <div class="editor">
        <p class="editor-help">
            <b>To indent, press Ctrl+]. To unindent, press Ctrl+[.</b>
            This helps with accessibility: you should be able to tab out of the editor.
        </p>
        <CodeMirror bind:editor />
    </div>
    <div class="footer">
        This website is not run by Microsoft or the Pyright maintainers.
    </div>
</main>

<style lang="scss">
    @import url("https://fonts.googleapis.com/css2?family=Roboto&display=swap");
    @import url("https://fonts.googleapis.com/css2?family=Roboto+Mono&display=swap");

    :global(.--sev-error) {
        --severity-hue: 0;
    }

    :global(.--sev-warning) {
        --severity-hue: 36;
    }

    :global(.--sev-information) {
        --severity-hue: 204;
    }

    :global(html, body) {
        width: 100vw;
        height: 100vh;
        padding: 0;
        margin: 0;
    }

    main {
        display: grid;
        grid-template-columns: 24em auto;
        grid-template-rows: 5em auto 8em;

        grid-template-areas:
            "title controls"
            "editor editor"
            "footer footer";

        overflow-x: hidden;
        height: 100%;
    }

    .title,
    .controls,
    .footer {
        display: flex;
        justify-content: center;
        align-items: center;
    }

    .generate-permalink,
    .github {
        padding: 1rem;
        font-size: 1.2rem;
    }

    .title {
        grid-area: title;

        font-family: "Roboto";
        font-size: 2rem;

        background-color: #6acbf1;
    }

    .controls {
        justify-content: space-between;
        padding-left: 3em;
        padding-righ: 3em;

        grid-area: controls;

        font-family: "Roboto";

        background-color: #9fd4e9;
    }

    .editor {
        > .editor-help {
            padding: 1em;
            font-size: 1rem;
            font-family: "Roboto";
        }
        grid-area: editor;
        font-size: 1.2rem;
        font-family: "Roboto Mono", monospace;
        --codemirror-min-height: 66vh;
    }

    .footer {
        color: #444;
        grid-area: footer;
    }
</style>
