import Foundation

/// Exhaustive error types for CLI process execution.
/// This is the contract between CLIRunner and all views.
enum CLIError: LocalizedError, Equatable {
    case binaryNotFound(searchedPaths: [String])
    case tokenMissing
    case tokenExpired
    case networkUnavailable
    case processTerminated(exitCode: Int32, stderr: String)
    case outputDecodingFailed(raw: String, message: String)
    case cancelled

    /// Short title for the error dialog header.
    var title: String {
        switch self {
        case .binaryNotFound: return "Binary Not Found"
        case .tokenMissing: return "Token Missing"
        case .tokenExpired: return "Token Expired"
        case .networkUnavailable: return "Network Unavailable"
        case .processTerminated: return "Command Failed"
        case .outputDecodingFailed: return "Output Error"
        case .cancelled: return "Cancelled"
        }
    }

    /// Human-readable summary (not the raw traceback).
    var summary: String {
        switch self {
        case .binaryNotFound(let paths):
            return "The ardl binary was not found in: \(paths.joined(separator: ", "))"
        case .tokenMissing:
            return "No Arista API token is configured."
        case .tokenExpired:
            return "Your Arista API token has expired."
        case .networkUnavailable:
            return "Could not connect to the Arista servers."
        case .processTerminated(let code, let stderr):
            // Extract the last meaningful line from stderr
            let meaningful = Self.extractMeaningfulError(from: stderr)
            return "The ardl command exited with code \(code).\n\n\(meaningful)"
        case .outputDecodingFailed(_, let message):
            return "Failed to decode CLI output: \(message)"
        case .cancelled:
            return "The operation was cancelled."
        }
    }

    /// Full stderr text for the collapsible detail section.
    var detailText: String? {
        switch self {
        case .processTerminated(_, let stderr):
            return stderr.isEmpty ? nil : stderr
        case .outputDecodingFailed(let raw, _):
            return raw.isEmpty ? nil : raw
        default:
            return nil
        }
    }

    var errorDescription: String? { summary }

    var recoverySuggestion: String? {
        switch self {
        case .binaryNotFound:
            return "Ensure ardl is bundled in Resources or available in PATH."
        case .tokenMissing:
            return "Go to Settings and enter your Arista API token."
        case .tokenExpired:
            return "Generate a new token at https://www.arista.com/en/users/profile"
        case .networkUnavailable:
            return "Check your internet connection and try again."
        case .processTerminated:
            return "Check the log output for details. If the issue persists, try running the command directly in a terminal."
        case .outputDecodingFailed:
            return "The CLI output format may have changed. Check for updates."
        case .cancelled:
            return nil
        }
    }

    /// Classify a process exit into a typed error by inspecting stderr content.
    static func from(exitCode: Int32, stderr: String) -> CLIError {
        let lower = stderr.lowercased()
        if lower.contains("token") || lower.contains("authentication") || lower.contains("401") {
            return .tokenExpired
        }
        if lower.contains("network") || lower.contains("connection") || lower.contains("timeout") {
            return .networkUnavailable
        }
        return .processTerminated(exitCode: exitCode, stderr: stderr)
    }

    /// Extract the last meaningful error line from a Python traceback or generic stderr.
    private static func extractMeaningfulError(from stderr: String) -> String {
        let lines = stderr.components(separatedBy: .newlines)
            .map { $0.trimmingCharacters(in: .whitespaces) }
            .filter { !$0.isEmpty }

        // For Python tracebacks, the last line is usually the actual error
        if stderr.contains("Traceback") {
            if let last = lines.last, !last.starts(with: "File ") && !last.starts(with: "~~~") {
                return last
            }
        }

        // Return last non-empty line, capped at 200 chars
        let lastLine = lines.last ?? "Unknown error"
        return String(lastLine.prefix(200))
    }
}
