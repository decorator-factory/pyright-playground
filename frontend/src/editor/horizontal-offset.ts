export const computeHorizontalOffset = (lines: string[], line: number, pos: number): number => {
    for (const l of lines.slice(0, line - 1)) {
        pos -= l.length;
    }
    return pos;
}

export const computePos = (lines: string[], line: number, col: number): number => {
    let pos = col;
    for (const l of lines.slice(0, line - 1)) {
        pos += l.length;
    }
    return pos;
}
