// swift-tools-version: 5.9

import PackageDescription

let package = Package(
    name: "EosDownloaderApp",
    platforms: [.macOS(.v13)],
    targets: [
        // Library target containing all testable code (models, CLI layer, views)
        .target(
            name: "EosDownloaderCore",
            path: "Sources/EosDownloaderCore"
        ),
        // Executable target — thin @main entry point only
        .executableTarget(
            name: "EosDownloaderApp",
            dependencies: ["EosDownloaderCore"],
            path: "Sources/EosDownloaderApp"
        ),
        .testTarget(
            name: "EosDownloaderAppTests",
            dependencies: ["EosDownloaderCore"],
            path: "Tests/EosDownloaderAppTests"
        ),
    ]
)
