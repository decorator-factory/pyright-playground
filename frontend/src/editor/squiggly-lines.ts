import { EditorView, Decoration, DecorationSet } from "@codemirror/view"
import { StateField, StateEffect } from "@codemirror/state"
import type { Diagnostic } from "../pyrightTypes"
import { computePos } from "./horizontal-offset"
import { RangeSet } from "@codemirror/rangeset"

const addUnderline = StateEffect.define<{ from: number; to: number }>()
const removeUnderlines = StateEffect.define()

const underlineField = StateField.define<DecorationSet>({
    create() {
        return Decoration.none
    },
    update(underlines, tr) {
        if (tr.docChanged) {
            return RangeSet.empty
        }

        underlines = underlines.map(tr.changes)
        for (let e of tr.effects)
            if (e.is(addUnderline)) {
                if (e.value.from >= e.value.to) continue

                underlines = underlines.update({
                    add: [underlineMark.range(e.value.from, e.value.to)],
                })
            }

        for (let e of tr.effects)
            if (e.is(removeUnderlines)) {
                underlines = RangeSet.empty
                break
            }

        return underlines
    },
    provide: (f) => EditorView.decorations.from(f),
})

const underlineMark = Decoration.mark({ class: "cm-underline" })

const underlineTheme = EditorView.baseTheme({
    ".cm-underline": {
        textDecoration: "underline 3px red",
        backgroundColor: "rgba(255, 0, 0, 0.1)",
    },
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
        }))
        .map(({ from, to }) => addUnderline.of({ from, to }))

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
