import Foundation

/// Locates the ardl binary in the app bundle or system PATH.
enum CLIBinaryLocator {

    /// Search order:
    /// 1. App bundle Resources/ardl_bundle/ardl
    /// 2. Custom path from UserDefaults
    /// 3. System PATH via /usr/bin/which
    static func locate() throws -> URL {
        var searchedPaths: [String] = []

        // 1. Bundled binary inside app Resources
        if let bundlePath = Bundle.main.resourceURL?
            .appendingPathComponent("ardl_bundle")
            .appendingPathComponent("ardl") {
            searchedPaths.append(bundlePath.path)
            if FileManager.default.isExecutableFile(atPath: bundlePath.path) {
                return bundlePath
            }
        }

        // 2. Custom path from user settings
        let customPath = UserDefaults.standard.string(forKey: "customArdlPath") ?? ""
        if !customPath.isEmpty {
            searchedPaths.append(customPath)
            if FileManager.default.isExecutableFile(atPath: customPath) {
                return URL(fileURLWithPath: customPath)
            }
        }

        // 3. System PATH lookup via which
        if let systemPath = findInSystemPath() {
            return systemPath
        }
        searchedPaths.append("$PATH")

        throw CLIError.binaryNotFound(searchedPaths: searchedPaths)
    }

    private static func findInSystemPath() -> URL? {
        let process = Process()
        let pipe = Pipe()
        process.executableURL = URL(fileURLWithPath: "/usr/bin/which")
        process.arguments = ["ardl"]
        process.standardOutput = pipe
        process.standardError = FileHandle.nullDevice

        do {
            try process.run()
            process.waitUntilExit()
            guard process.terminationStatus == 0 else { return nil }

            let data = pipe.fileHandleForReading.readDataToEndOfFile()
            guard let path = String(data: data, encoding: .utf8)?
                .trimmingCharacters(in: .whitespacesAndNewlines),
                  !path.isEmpty else { return nil }

            return URL(fileURLWithPath: path)
        } catch {
            return nil
        }
    }
}
