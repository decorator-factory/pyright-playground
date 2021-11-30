export type PyrightOutput = {
    version: string
    time: string
    generalDiagnostics: Diagnostic[]
    summary: {
        filesAnalyzed: number
        errorCount: number
        warningCount: number
        informationCount: number
        timeInSec: number
    }
}

export type Diagnostic = {
    file: string
    severity: "error" | "warning" | "information"
    message: string
    rule?: string
    range: {
        start: {
            line: number
            character: number
        }
        end: {
            line: number
            character: number
        }
    }
}
