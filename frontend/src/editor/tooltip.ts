import { Tooltip, showTooltip } from "@codemirror/tooltip"
import { StateEffect, StateField } from "@codemirror/state"
import { EditorState, EditorView } from "@codemirror/basic-setup"
import type { Diagnostic } from "../pyrightTypes"
import { computeHorizontalOffset } from "./horizontal-offset"

const cursorTooltipBaseTheme = EditorView.baseTheme({
    ".cm-tooltip.cm-tooltip-cursor": {
        backgroundColor: "hsla(var(--severity-hue), 65%, 35%)",
        color: "white",
        border: "none",
        padding: "0.5em",
        borderRadius: "4px",
        "&.cm-tooltip-arrow:before": {
            borderTopColor: "hsla(var(--severity-hue), 65%, 35%)",
        },
        "&.cm-tooltip-arrow:after": {
            borderTopColor: "transparent",
        },
    },
    ".cm-monospace-message": {
        whiteSpace: "pre-wrap",
        fontFamily: "'Roboto Mono', monospace",
    },
    ".cm-severity-icon": {
        width: "0.66em",
        height: "0.66em",
        filter: "invert(100%)",
        marginRight: "0.33em",
    },
})

export const diagnosticsArrived = StateEffect.define<Diagnostic[]>()

export const diagnosticsField = StateField.define<Readonly<
    Diagnostic[]
> | null>({
    create: () => null,

    update(oldValue, transaction) {
        const effect = transaction.effects.find((e) => e.is(diagnosticsArrived))
        if (effect === undefined) return oldValue
        return effect.value
    },
})

const getCursorTooltips = (state: EditorState): readonly Tooltip[] => {
    const diagnostics = state.field(diagnosticsField)

    if (diagnostics === null) return []

    return state.selection.ranges.flatMap((range) => {
        const line = state.doc.lineAt(range.head).number
        const codeLines = state.doc.toJSON()
        const minCol = computeHorizontalOffset(codeLines, line, range.from)
        const maxCol = computeHorizontalOffset(codeLines, line, range.to)
        const diagnosticsToShow = diagnostics.filter(
            (diag) =>
                diag.range.start.line + 1 <= line &&
                diag.range.end.line + 1 >= line &&
                diag.range.start.character <= minCol &&
                diag.range.end.character >= maxCol,
        )

        return diagnosticsToShow.map((diag) => ({
            pos: range.head,
            above: false,
            strictSide: true,
            arrow: true,
            create: () => {
                const tooltip = document.createElement("div")
                tooltip.className = `cm-tooltip-cursor --sev-${diag.severity}`

                const icon = document.createElement("img")
                icon.className = "cm-severity-icon"
                icon.src = `/icons/severity-${diag.severity}.svg`

                const message = document.createElement("span")
                message.className = "cm-monospace-message"
                message.appendChild(icon)
                message.appendChild(document.createTextNode(diag.message))

                tooltip.appendChild(icon)
                tooltip.appendChild(message)
                return { dom: tooltip }
            },
        }))
    })
}

const cursorTooltipField = StateField.define<readonly Tooltip[]>({
    create: getCursorTooltips,

    update(tooltips, tr) {
        if (!tr.docChanged && !tr.selection) return tooltips
        return getCursorTooltips(tr.state)
    },

    provide: (f) => showTooltip.computeN([f], (state) => state.field(f)),
})

export const cursorTooltip = () => {
    return [diagnosticsField, cursorTooltipField, cursorTooltipBaseTheme]
}
