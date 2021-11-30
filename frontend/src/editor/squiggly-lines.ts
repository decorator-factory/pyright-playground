import { EditorView, Decoration, DecorationSet } from "@codemirror/view"
import { StateField, StateEffect } from "@codemirror/state"
import type { Diagnostic } from "../pyrightTypes"
import { computePos } from "./horizontal-offset"
import { RangeSet } from "@codemirror/rangeset"

const addUnderline =
    StateEffect.define<{
        from: number
        to: number
        severity: "error" | "warning" | "information"
    }>()
const removeUnderlines = StateEffect.define()

const underlineField = StateField.define<DecorationSet>({
    create() {
        return Decoration.none
    },
    update(underlines, tr) {
        if (tr.docChanged) return RangeSet.empty

        for (let e of tr.effects)
            if (e.is(removeUnderlines)) return RangeSet.empty

        for (let e of tr.effects)
            if (e.is(addUnderline)) {
                if (e.value.from >= e.value.to) continue
                if (e.value.to > tr.newDoc.length) continue

                underlines = underlines.update({
                    add: [
                        underlineMark[e.value.severity].range(
                            e.value.from,
                            e.value.to,
                        ),
                    ],
                })
            }

        return underlines
    },
    provide: (f) => EditorView.decorations.from(f),
})

const underlineMark = {
    error: Decoration.mark({ class: "cm-underline --error" }),
    warning: Decoration.mark({ class: "cm-underline --warning" }),
    information: Decoration.mark({ class: "cm-underline --information" }),
}

const underlineTheme = EditorView.baseTheme({
    ".cm-underline": {
        textDecoration:
            "underline 3px hsla(var(--cm-underline-hue), 100%, 50%, 1)",
        backgroundColor: "hsla(var(--cm-underline-hue), 100%, 50%, 0.1)",
    },

    ".--error": { "--cm-underline-hue": "0" },
    ".--warning": { "--cm-underline-hue": "36" },
    ".--information": { "--cm-underline-hue": "204" },
})

export const addSquigglyLines = (
    view: EditorView,
    diagostics: Diagnostic[],
) => {
    const lines = view.state.doc.toJSON()

    const effects: StateEffect<unknown>[] = diagostics
        .map((diag) => ({
            from: computePos(
                lines,
                diag.range.start.line + 1,
                diag.range.start.character,
            ),
            to: computePos(
                lines,
                diag.range.end.line + 1,
                diag.range.end.character,
            ),
            severity: diag.severity,
        }))
        .map((spec) => addUnderline.of(spec))

    if (effects.length === 0) return

    if (!view.state.field(underlineField, false))
        effects.push(
            StateEffect.appendConfig.of([underlineField, underlineTheme]),
        )

    view.dispatch({ effects })
}

export const resetSquigglyLines = (view: EditorView) => {
    const effects: StateEffect<unknown>[] = [removeUnderlines.of(null)]

    if (!view.state.field(underlineField, false))
        effects.push(
            StateEffect.appendConfig.of([underlineField, underlineTheme]),
        )

    view.dispatch({ effects })
}
