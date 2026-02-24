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

    var errorDescription: String? {
        switch self {
        case .binaryNotFound(let paths):
            return "ardl binary not found in: \(paths.joined(separator: ", "))"
        case .tokenMissing:
            return "Arista API token not configured"
        case .tokenExpired:
            return "Arista API token has expired"
        case .networkUnavailable:
            return "Network connection unavailable"
        case .processTerminated(let code, let stderr):
            let detail = stderr.isEmpty ? "" : ": \(stderr.prefix(200))"
            return "CLI process exited with code \(code)\(detail)"
        case .outputDecodingFailed(_, let message):
            return "Failed to decode CLI output: \(message)"
        case .cancelled:
            return "Operation was cancelled"
        }
    }

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
            return "Check the log output for details."
        case .outputDecodingFailed:
            return "The CLI output format may have changed. Check for updates."
        case .cancelled:
            return nil
        }
    }

    /// Classify a process exit into a typed error by inspecting stderr content.
    static func from(exitCode: Int32, stderr: String) -> CLIError {
        let lower = stderr.lowercased()
        if lower.contains("authentication error") || lower.contains("401") {
            return .tokenExpired
        }
        if lower.contains("network") || lower.contains("connection") || lower.contains("timeout") {
            return .networkUnavailable
        }
        return .processTerminated(exitCode: exitCode, stderr: stderr)
    }
}
