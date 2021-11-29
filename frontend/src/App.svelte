<script lang="ts">
import {onMount} from "svelte";
import * as monaco from "monaco-editor";

export let apiEndpoint: string;

let container: HTMLElement;

type PyrightOutput = {
    version: string,
    time: string,
    generalDiagnostics: Diagnostic[],
    summary: {
        filesAnalyzed: number,
        errorCount: number,
        warningCount: number,
        informationCount: number,
        timeInSec: number
    }
};

type Diagnostic = {
    file: string,
    severity: 'error' | 'warning' | 'information',
    message: string,
    rule?: string,
    range: {
        start: {
            line: number,
            character: number
        },
        end: {
            line: number,
            character: number
        }
    }
};


let lastUpdatedMs = Date.now() - 1000;
let updateTimeoutId: any = -1;


const fetchAndApplyPyrightDiagnostic = async (editor: monaco.editor.IStandaloneCodeEditor) => {
    const code = editor.getValue();
    const resp = await fetch(apiEndpoint, {method: "POST", body: JSON.stringify({code})});
    const pyrightOutput: PyrightOutput = await resp.json();

    let markers = pyrightOutput.generalDiagnostics.map(diag => ({
        severity: {
            error: monaco.MarkerSeverity.Error,
            warning: monaco.MarkerSeverity.Warning,
            information: monaco.MarkerSeverity.Info,
        }[diag.severity],

        message: diag.message,

        startLineNumber: diag.range.start.line + 1,
        startColumn: diag.range.start.character + 1,
        endLineNumber: diag.range.end.line + 1,
        endColumn: diag.range.end.character + 1,
    }));

    monaco.editor.setModelMarkers(editor.getModel()!, "owner", markers);
}


const updateEditor = async (editor: monaco.editor.IStandaloneCodeEditor) => {
    const diff = Date.now() - lastUpdatedMs;
    if (diff < 1000) {
        if (updateTimeoutId !== -1)
            clearTimeout(updateTimeoutId);
        updateTimeoutId = setTimeout(() => updateEditor(editor), 1000 - diff);
        return;
    }
    lastUpdatedMs = Date.now();
    await fetchAndApplyPyrightDiagnostic(editor);
};


onMount(() => {
    const editor = monaco.editor.create(
        container,
        {
            value: "def f(x: int) -> str:\n    return x",
            language: 'python',
            automaticLayout: true,
        }
    );

    updateEditor(editor);

    editor.getModel()!.onDidChangeContent(async (event) => {
        await updateEditor(editor);
    });
})

</script>

<main>
    <div class="title">Pyright playground</div>
    <div class="controls">Controls (TODO)</div>
    <div class="editor">
        <div class="editor-container" bind:this={container}></div>
    </div>
    <div class="footer">BTW: This website is not run by Microsoft or the Pyright maintainers.</div>
</main>

<style lang="scss">
@import url('https://fonts.googleapis.com/css2?family=Roboto&display=swap');

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
        "footer footer"
    ;

    overflow-x: hidden;
    height: 100%;
}

.title, .controls, .footer {
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
    padding-top: 2em;
    grid-area: editor;

    >.editor-container{
        height: 100%;
    }
}

.footer {
    grid-area: footer;
}
</style>