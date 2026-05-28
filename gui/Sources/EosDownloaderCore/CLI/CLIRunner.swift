import Foundation

/// Thread-safe CLI process runner using Swift actor isolation.
/// Wraps Foundation.Process for async/await execution of the ardl binary.
actor CLIRunner {

    private var currentProcess: Process?

    /// Run a CLI command and capture the full output.
    /// Token is passed via ARISTA_TOKEN environment variable (never as --token arg).
    func run(args: [String], env: [String: String] = [:]) async throws -> CLIResult {
        let binaryURL = try CLIBinaryLocator.locate()

        let process = Process()
        let stdoutPipe = Pipe()
        let stderrPipe = Pipe()

        process.executableURL = binaryURL
        process.arguments = args
        process.standardOutput = stdoutPipe
        process.standardError = stderrPipe

        // Merge custom env (ARISTA_TOKEN) with inherited environment
        var processEnv = ProcessInfo.processInfo.environment
        for (key, value) in env {
            processEnv[key] = value
        }
        process.environment = processEnv

        currentProcess = process

        return try await withTaskCancellationHandler {
            try await withCheckedThrowingContinuation { continuation in
                do {
                    process.terminationHandler = { terminatedProcess in
                        let stdoutData = stdoutPipe.fileHandleForReading.readDataToEndOfFile()
                        let stderrData = stderrPipe.fileHandleForReading.readDataToEndOfFile()

                        let result = CLIResult(
                            exitCode: terminatedProcess.terminationStatus,
                            stdout: String(data: stdoutData, encoding: .utf8) ?? "",
                            stderr: String(data: stderrData, encoding: .utf8) ?? ""
                        )
                        continuation.resume(returning: result)
                    }
                    try process.run()
                } catch {
                    continuation.resume(throwing: CLIError.processTerminated(
                        exitCode: -1,
                        stderr: error.localizedDescription
                    ))
                }
            }
        } onCancel: {
            process.terminate()
        }
    }

    /// Stream CLI output line by line for long-running operations (downloads).
    /// Each line is stripped of ANSI escape codes before delivery.
    func stream(
        args: [String],
        env: [String: String] = [:],
        onLine: @escaping @Sendable (String) -> Void
    ) async throws -> CLIResult {
        let binaryURL = try CLIBinaryLocator.locate()

        let process = Process()
        let stdoutPipe = Pipe()
        let stderrPipe = Pipe()

        process.executableURL = binaryURL
        process.arguments = args
        process.standardOutput = stdoutPipe
        process.standardError = stderrPipe

        var processEnv = ProcessInfo.processInfo.environment
        for (key, value) in env {
            processEnv[key] = value
        }
        process.environment = processEnv

        currentProcess = process

        // Thread-safe accumulator for stdout chunks
        final class Accumulator: @unchecked Sendable {
            private let lock = NSLock()
            private var storage = ""
            func append(_ text: String) { lock.lock(); storage += text; lock.unlock() }
            var value: String { lock.lock(); defer { lock.unlock() }; return storage }
        }

        let accumulator = Accumulator()
        stdoutPipe.fileHandleForReading.readabilityHandler = { handle in
            let data = handle.availableData
            guard !data.isEmpty else { return }
            if let chunk = String(data: data, encoding: .utf8) {
                accumulator.append(chunk)
                let lines = chunk.components(separatedBy: .newlines)
                for line in lines where !line.isEmpty {
                    onLine(Self.stripANSI(line))
                }
            }
        }

        return try await withTaskCancellationHandler {
            try await withCheckedThrowingContinuation { continuation in
                do {
                    process.terminationHandler = { terminatedProcess in
                        stdoutPipe.fileHandleForReading.readabilityHandler = nil
                        let stderrData = stderrPipe.fileHandleForReading.readDataToEndOfFile()

                        let result = CLIResult(
                            exitCode: terminatedProcess.terminationStatus,
                            stdout: accumulator.value,
                            stderr: String(data: stderrData, encoding: .utf8) ?? ""
                        )
                        continuation.resume(returning: result)
                    }
                    try process.run()
                } catch {
                    continuation.resume(throwing: CLIError.processTerminated(
                        exitCode: -1,
                        stderr: error.localizedDescription
                    ))
                }
            }
        } onCancel: {
            process.terminate()
        }
    }

    /// Cancel the currently running process.
    func cancel() {
        currentProcess?.terminate()
        currentProcess = nil
    }

    /// Strip ANSI escape codes from a string.
    static func stripANSI(_ input: String) -> String {
        input.replacingOccurrences(
            of: "\\x1B\\[[0-9;]*[mGKHF]",
            with: "",
            options: .regularExpression
        )
    }
}
