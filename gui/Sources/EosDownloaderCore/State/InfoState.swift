import Foundation

/// Observable state for all Info tab queries.
/// Shared across VersionListView, LatestVersionView, and MappingView
/// so filter selections (package, branch, releaseType) are consistent.
final class InfoState: ObservableObject {

    // MARK: - Shared filter parameters

    @Published var package: String = "eos"
    @Published var branch: String = ""
    @Published var releaseType: String = "F"

    // MARK: - Versions tab

    @Published var versions: [VersionEntry] = []
    @Published var isLoadingVersions: Bool = false
    @Published var versionsError: CLIError?

    // MARK: - Latest tab

    @Published var latest: LatestVersion? = nil
    @Published var isLoadingLatest: Bool = false
    @Published var latestError: CLIError?

    // MARK: - Mapping tab

    @Published var mapping: MappingResponse = [:]
    @Published var isLoadingMapping: Bool = false
    @Published var mappingError: CLIError?

    private let runner = CLIRunner()

    // MARK: - Fetch actions

    /// Fetch `ardl info versions --package <pkg> [--branch <b>] [--release-type <r>] --format json`
    @MainActor
    func fetchVersions() async {
        guard !isLoadingVersions else { return }
        isLoadingVersions = true
        versionsError = nil
        versions = []

        do {
            let token = try KeychainTokenManager.requireToken()
            var args = ["info", "versions", "--package", package, "--format", "json"]
            // CVP has no release type concept; only pass for EOS
            if package == "eos" { args += ["--release-type", releaseType] }
            if !branch.isEmpty { args += ["--branch", branch] }

            let result = try await runner.run(args: args, env: ["ARISTA_TOKEN": token])
            if result.succeeded {
                versions = try result.decode([VersionEntry].self)
            } else {
                versionsError = CLIError.from(exitCode: result.exitCode, stderr: result.stderr)
            }
        } catch let e as CLIError {
            versionsError = e
        } catch {
            versionsError = .processTerminated(exitCode: -1, stderr: error.localizedDescription)
        }

        isLoadingVersions = false
    }

    /// Fetch `ardl info latest --package <pkg> [--branch <b>] [--release-type <r>] --format json`
    @MainActor
    func fetchLatest() async {
        guard !isLoadingLatest else { return }
        isLoadingLatest = true
        latestError = nil
        latest = nil

        do {
            let token = try KeychainTokenManager.requireToken()
            var args = ["info", "latest", "--package", package, "--format", "json"]
            // CVP has no release type concept; only pass for EOS
            if package == "eos" { args += ["--release-type", releaseType] }
            if !branch.isEmpty { args += ["--branch", branch] }

            let result = try await runner.run(args: args, env: ["ARISTA_TOKEN": token])
            if result.succeeded {
                latest = try result.decode(LatestVersion.self)
            } else {
                latestError = CLIError.from(exitCode: result.exitCode, stderr: result.stderr)
            }
        } catch let e as CLIError {
            latestError = e
        } catch {
            latestError = .processTerminated(exitCode: -1, stderr: error.localizedDescription)
        }

        isLoadingLatest = false
    }

    /// Fetch `ardl info mapping --package <pkg> --format json`
    /// No token required — mapping is derived from local software_mapping constants.
    @MainActor
    func fetchMapping() async {
        guard !isLoadingMapping else { return }
        isLoadingMapping = true
        mappingError = nil
        mapping = [:]

        do {
            let args = ["info", "mapping", "--package", package, "--format", "json"]
            let result = try await runner.run(args: args, env: [:])
            if result.succeeded {
                mapping = try result.decode(MappingResponse.self)
            } else {
                mappingError = CLIError.from(exitCode: result.exitCode, stderr: result.stderr)
            }
        } catch let e as CLIError {
            mappingError = e
        } catch {
            mappingError = .processTerminated(exitCode: -1, stderr: error.localizedDescription)
        }

        isLoadingMapping = false
    }
}
