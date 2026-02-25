import Foundation
import SwiftUI

/// Observable state for the EOS download form.
/// Each download view gets its own instance to avoid cross-form interference.
final class DownloadState: ObservableObject {

    // MARK: - EOS Form Fields

    @Published var selectedFormat: String = "64"
    @Published var version: String = ""
    @Published var useLatest: Bool = false
    @Published var branch: String = ""
    @Published var releaseType: String = "F"
    @Published var outputPath: String = defaultOutputPath

    // Docker options
    @Published var importDocker: Bool = false
    @Published var dockerName: String = "arista/ceos"
    @Published var dockerTag: String = "latest"

    // Flags
    @Published var dryRun: Bool = false
    @Published var force: Bool = false
    @Published var eveNg: Bool = false

    // MARK: - Execution State

    @Published var isRunning: Bool = false
    @Published var logLines: [String] = []
    @Published var currentError: CLIError?
    @Published var progress: DownloadProgress = DownloadProgress()

    private let cliRunner = CLIRunner()
    private var downloadTask: Task<Void, Never>?

    static var defaultOutputPath: String {
        FileManager.default.urls(for: .downloadsDirectory, in: .userDomainMask)
            .first?.path ?? "~/Downloads"
    }

    /// Available EOS image formats.
    static let eosFormats = [
        "64", "INT", "2GB-INT", "cEOS", "cEOS64", "cEOSarm",
        "vEOS", "vEOS-lab", "vEOS64-lab", "vEOS64-lab-qcow2", "vEOS64-lab-swi",
        "EOS-2GB", "RN", "SOURCE"
    ]

    static let releaseTypes = ["F", "M"]

    // MARK: - Actions

    /// Build CLI arguments from current form state.
    func buildArguments() -> [String] {
        var args = ["get", "eos", "--format", selectedFormat]

        if useLatest {
            args.append("--latest")
        } else if !version.isEmpty {
            args += ["--version", version]
        }

        if !branch.isEmpty {
            args += ["--branch", branch]
        }

        args += ["--release-type", releaseType]
        args += ["--output", outputPath]

        if importDocker {
            args.append("--import-docker")
            args += ["--docker-name", dockerName]
            args += ["--docker-tag", dockerTag]
        }

        if eveNg { args.append("--eve-ng") }
        if dryRun { args.append("--dry-run") }
        if force { args.append("--force") }

        return args
    }

    /// Start the download process.
    @MainActor
    func startDownload() {
        guard !isRunning else { return }

        isRunning = true
        logLines = []
        currentError = nil
        progress = DownloadProgress()

        downloadTask = Task {
            do {
                let token = try KeychainTokenManager.requireToken()
                let args = buildArguments()

                logLines.append("Running: ardl \(args.joined(separator: " "))")

                let result = try await cliRunner.stream(
                    args: args,
                    env: ["ARISTA_TOKEN": token]
                ) { [weak self] line in
                    Task { @MainActor in
                        self?.logLines.append(line)
                        self?.progress.update(from: line)
                    }
                }

                await MainActor.run {
                    if result.succeeded {
                        logLines.append("Download completed successfully.")
                        progress.phase = .completed
                        progress.percentage = 100
                    } else {
                        let error = CLIError.from(exitCode: result.exitCode, stderr: result.stderr)
                        currentError = error
                        logLines.append("Error: \(error.localizedDescription)")
                        progress.phase = .failed
                    }
                    isRunning = false
                }
            } catch let error as CLIError {
                await MainActor.run {
                    currentError = error
                    logLines.append("Error: \(error.localizedDescription)")
                    progress.phase = .failed
                    isRunning = false
                }
            } catch {
                await MainActor.run {
                    currentError = .processTerminated(exitCode: -1, stderr: error.localizedDescription)
                    progress.phase = .failed
                    isRunning = false
                }
            }
        }
    }

    /// Cancel the running download.
    @MainActor
    func cancelDownload() {
        downloadTask?.cancel()
        downloadTask = nil
        Task {
            await cliRunner.cancel()
        }
        logLines.append("Download cancelled.")
        progress.phase = .failed
        isRunning = false
    }
}
