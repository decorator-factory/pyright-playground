<script lang="ts">
    import CodeMirror from "./editor/CodeMirror.svelte"
    import type { Editor } from "./editor"
    import type { PyrightOutput } from "./pyrightTypes"

    import { onMount } from "svelte"

    export let apiEndpoint: string

    const lineAndColToPos = (line: number, col: number, code: string) => {
        const lines = code.split("\n")
        if (lines.length < line) return code.length - 1
        const lengthSoFar = lines
            .slice(0, line + 1)
            .reduce((a, line) => a + line.length, 0)
        return lengthSoFar + col
    }

    let lastUpdatedMs = Date.now() - 1000
    let updateTimeoutId: any = -1
    let editor: Editor

    const fetchAndApplyPyrightDiagnostic = async () => {
        const code = editor.read()
        const resp = await fetch(apiEndpoint, {
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
        if (diff < 1000) {
            if (updateTimeoutId !== -1) clearTimeout(updateTimeoutId)
            updateTimeoutId = setTimeout(updateEditor, 1000 - diff)
            return
        }
        lastUpdatedMs = Date.now()
        await fetchAndApplyPyrightDiagnostic()
    }

    onMount(() => {
        editor.onUpdate(async (update) => {
            if (!update.docChanged) return

            await updateEditor()
        })

        updateEditor()
    })
</script>

<main>
    <div class="title">Pyright playground</div>
    <div class="controls">Controls (TODO)</div>
    <div class="editor">
        <p class="editor-help">
            <b>To indent, press Ctrl+]. To unindent, press Ctrl+[.</b>
            This helps with accessibility: you should be able to tab out of the editor.
        </p>
        <CodeMirror bind:editor />
    </div>
    <div class="footer">
        BTW: This website is not run by Microsoft or the Pyright maintainers.
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

    .title {
        grid-area: title;

        font-family: "Roboto";
        font-size: 2rem;

        background-color: #6acbf1;
    }

    .controls {
        justify-content: start;
        padding-left: 3em;

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
        font-size: 1.3rem;
        font-family: "Roboto Mono", monospace;
        --codemirror-min-height: 50vh;
    }

    .footer {
        grid-area: footer;
    }
</style>
