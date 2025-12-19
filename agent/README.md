# Agent

Agent client application that connects to Master server.

## Running the Agent

### Quick Start

Use the provided script (recommended):

```bash
./run.sh
```

### Manual Run

To run the agent manually, explicitly specify the project:

```bash
dotnet run --project Agent.csproj
```

### Troubleshooting Build Errors

If you encounter build errors (especially related to duplicate assembly attributes or missing test dependencies):

```bash
# Clean all build artifacts
rm -rf obj bin Agent.Tests/obj Agent.Tests/bin

# Restore dependencies for all projects (including test project)
dotnet restore

# Build and run the agent (explicitly specifying the project)
dotnet build Agent.csproj --no-restore
dotnet run --project Agent.csproj --no-build
```

**Note**: The test project dependencies (Moq, Xunit) are restored when running `dotnet restore` from the agent directory. This ensures all project dependencies are available even if only building the main Agent project.

## Building

To build the agent:

```bash
dotnet build Agent.csproj
```

## Running Tests

To run tests, first restore dependencies, then test:

```bash
dotnet restore
dotnet test Agent.Tests/Agent.Tests.csproj
```

