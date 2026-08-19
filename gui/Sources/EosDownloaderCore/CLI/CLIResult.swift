import Foundation

/// Result of a CLI process execution.
struct CLIResult {
    let exitCode: Int32
    let stdout: String
    let stderr: String

    var succeeded: Bool { exitCode == 0 }

    /// Decode stdout as JSON into a Codable type.
    func decode<T: Decodable>(_ type: T.Type) throws -> T {
        guard let data = stdout.data(using: .utf8) else {
            throw CLIError.outputDecodingFailed(raw: stdout, message: "Invalid UTF-8")
        }
        do {
            return try JSONDecoder().decode(type, from: data)
        } catch {
            throw CLIError.outputDecodingFailed(
                raw: String(stdout.prefix(500)),
                message: error.localizedDescription
            )
        }
    }
}
