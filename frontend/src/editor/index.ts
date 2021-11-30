import {
    keymap,
    highlightSpecialChars,
    drawSelection,
    highlightActiveLine,
    EditorView,
    ViewUpdate,
} from "@codemirror/view"
import { Extension, EditorState } from "@codemirror/state"
import { history, historyKeymap } from "@codemirror/history"
import { foldGutter, foldKeymap } from "@codemirror/fold"
import { indentUnit } from "@codemirror/language"
import { lineNumbers } from "@codemirror/gutter"
import { defaultKeymap } from "@codemirror/commands"
import { bracketMatching } from "@codemirror/matchbrackets"
import { closeBrackets, closeBracketsKeymap } from "@codemirror/closebrackets"
import { searchKeymap, highlightSelectionMatches } from "@codemirror/search"
import { autocompletion, completionKeymap } from "@codemirror/autocomplete"
import { commentKeymap } from "@codemirror/comment"
import { rectangularSelection } from "@codemirror/rectangular-selection"
import { defaultHighlightStyle } from "@codemirror/highlight"
import { lintKeymap } from "@codemirror/lint"
import { python } from "@codemirror/lang-python"
import { cursorTooltip, diagnosticsArrived } from "./tooltip"
import type { Diagnostic } from "../pyrightTypes"
import { addSquigglyLines, resetSquigglyLines } from "./squiggly-lines"

const basicSetup = [
    lineNumbers(),
    highlightSpecialChars(),
    history(),
    foldGutter(),
    drawSelection(),
    EditorState.allowMultipleSelections.of(true),
    indentUnit.of("    "),
    defaultHighlightStyle.fallback,
    bracketMatching(),
    closeBrackets(),
    autocompletion(),
    rectangularSelection(),
    highlightActiveLine(),
    highlightSelectionMatches(),
    keymap.of([
        ...closeBracketsKeymap,
        ...defaultKeymap,
        ...searchKeymap,
        ...historyKeymap,
        ...foldKeymap,
        ...commentKeymap,
        ...completionKeymap,
        ...lintKeymap,
    ]),
]

export interface Editor {
    view: EditorView
    read: () => string
    onUpdate: (handler: (_: ViewUpdate) => void) => void
    applyDiagnostics: (diagnostics: Diagnostic[]) => void
}

export const makeEditor = (...exts: Extension[]): Editor => {
    const theme = EditorView.theme({
        ".cm-activeLine": {
            backgroundColor: "var(--codemirror-active-line)",
        },
        ".cm-content": {
            minHeight: "var(--codemirror-min-height)",
        },
        ".cm-scroller": {
            overflow: "hidden",
        },
        ".cm-gutter": {
            backgroundColor: "var(--codemirror-gutter-color)",
        },
        ".cm-wrap": {
            minHeight: "var(--codemirror-min-height)",
            border: "1px solid silver",
        },
    })

    const updateListeners: ((_: ViewUpdate) => void)[] = []
    const updateListener = EditorView.updateListener.of((update) =>
        updateListeners.forEach((f) => f(update)),
    )

    const startState = EditorState.create({
        doc: "def f(foooo: int) -> str:\n    return foooo",
        extensions: [
            ...basicSetup,
            ...exts,
            python(),
            ...cursorTooltip(),
            theme,
            updateListener,
        ],
    })

    const view = new EditorView({
        state: startState,
    })

    return {
        view,
        read: (): string => view.state.doc.toJSON().join("\n"),
        onUpdate: (handler) => updateListeners.push(handler),
        applyDiagnostics: (diagnostics) => {
            resetSquigglyLines(view)
            addSquigglyLines(view, diagnostics)
            view.dispatch({ effects: diagnosticsArrived.of(diagnostics) })
        },
    }
}
